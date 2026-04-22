import json
import traceback
from threading import Thread
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.core.security import get_current_user
from app.db.session import SessionLocal,get_db
from app.models.identity import User
from app.models.lead import FollowupRecord,Lead
from app.models.procurement import PurchaseRequest,Quote,RFQ
from app.models.proposal import ProposalProject
from app.models.supplier import Supplier,SupplierEvaluation
from app.schemas.ai import AIExecuteRequest
from app.schemas.common import APIResponse
from app.services.ai_task_service import AITaskService
from app.services.audit_service import AuditService
from app.services.knowledge_service import KnowledgeService
from app.services.orchestrator import AgentOrchestratorService
router=APIRouter();service=AgentOrchestratorService()
def _kg(db:Session,scene:str,ctx:dict)->dict:
 p=dict(ctx);p['knowledge_sources']=KnowledgeService(db).retrieve_sources(scene=scene,limit=3);return p
def _lead_status(score:float,m:str,s:str)->str:
 s=(s or 'new').strip().lower()
 if s in {'won','lost','invalid','archived'}:return s
 if score>=85:return 'qualified'
 if score>=60 or m in {'high','medium'}:return 'contacted'
 return s or 'new'
def _top(items,defaults,limit=None):
 values=[str(i).strip() for i in (items or []) if str(i).strip()]
 picked=values or list(defaults)
 return picked[:limit] if limit else picked
def _outline(t):
 r=_top(t.recommendations,['提炼项目背景与招标目标','梳理建设范围与能力映射','形成实施计划与保障机制','补充风险控制与偏差说明'])
 n=_top(t.next_actions,['补齐需求映射表','细化里程碑计划','补充验收与培训安排'],3)
 e=_top(t.evidence,['需对关键风险条款做专项澄清','需补充交付边界说明','需结合案例增强可信度'],3)
 return '\n'.join(['方案大纲','','一、项目理解与建设目标\n1. 项目背景与目标\n2. 业务痛点与建设价值\n3. 招标关注点与投标策略','','二、总体解决方案\n1. 总体架构说明\n2. 核心能力映射\n3. 差异化优势','','三、实施与交付计划\n1. 项目组织与角色分工\n2. 里程碑与进度安排\n3. 验收、培训与运维保障','','四、风险与应对\n'+'\n'.join([f'- {i}' for i in e]),'','五、建议优先展开章节\n'+'\n'.join([f'- {i}' for i in r]),'','六、下一步写作动作\n'+'\n'.join([f'- {i}' for i in n])])
def _tech(t):
 n=_top(t.next_actions,['梳理系统架构与部署方案','逐条映射招标技术要求','补充实施与验收计划','完善安全与运维方案'])
 r=_top(t.recommendations,['突出方案完整性与可落地性','按评分点组织技术章节','用案例强化能力证明'],3)
 e=_top(t.evidence,['当前需进一步细化接口与性能指标','需补充行业案例与项目经验','需明确风险应对与质量保障'],3)
 return '\n'.join(['技术方案草稿','','1. 项目技术理解\n本方案基于当前招标信息，对建设目标、业务流程、关键能力与交付边界进行统一梳理，重点确保技术路线与评分要求保持一致。','','2. 总体技术方案\n- 建议采用分层架构组织能力模块，兼顾扩展性、稳定性与后续维护效率。\n- 对核心业务流程、接口协同、权限控制、日志审计与数据管理进行统一设计。\n- 在实施阶段同步考虑测试、上线、培训和运维衔接。','','3. 重点技术工作\n'+'\n'.join([f'- {i}' for i in n]),'','4. 技术应答建议\n'+'\n'.join([f'- {i}' for i in r]),'','5. 当前需补充的能力证明\n'+'\n'.join([f'- {i}' for i in e]),'','6. 交付与保障\n- 建议补齐实施组织、质量控制、风险预案、试运行、验收标准与运维承诺等章节。'])
def _biz(t):
 e=_top(t.evidence,['需明确关键条款偏差说明','需补充服务边界与承诺口径','需控制商务风险暴露'],4)
 r=_top(t.recommendations,['围绕评分规则组织商务应答','明确报价逻辑与服务清单','对高风险条款形成澄清策略'],3)
 n=_top(t.next_actions,['补充报价说明与测算依据','梳理付款与验收节点','形成商务偏差表'],3)
 return '\n'.join(['商务方案草稿','','1. 商务响应原则\n本商务方案围绕招标文件条款响应、报价策略、服务承诺、交付保障及风险控制进行组织，确保整体口径清晰、边界明确、可审计可复核。','','2. 商务应答重点\n'+'\n'.join([f'- {i}' for i in r]),'','3. 重点风险条款\n'+'\n'.join([f'- {i}' for i in e]),'','4. 建议补充的商务材料\n'+'\n'.join([f'- {i}' for i in n]),'','5. 服务与交付承诺\n- 建议明确项目组织机制、响应时效、保修周期、驻场/远程支持边界及升级路径。\n- 对关键付款节点、验收条件、违约责任、知识产权与保密条款进行逐项核对。'])
def _risk(c:float)->str:return 'low' if c>=.85 else 'medium' if c>=.65 else 'high'
def _score(c:float,h:float,m:float,l:float)->float:return h if c>=.85 else m if c>=.65 else l
def _resp(t):return {'task_id':t.task_id,'scene':t.scene,'agent_name':t.agent_name,'provider':t.provider,'status':t.status,'summary':t.summary,'recommendations':t.recommendations,'evidence':t.evidence,'insights':t.insights,'next_actions':t.next_actions,'raw_output':{'fallback':t.raw_output.get('fallback')} if t.status=='degraded' else t.raw_output,'context':t.context,'degraded':t.degraded,'error_message':t.error_message,'created_at':t.created_at.isoformat() if t.created_at else None,'completed_at':t.completed_at.isoformat() if t.completed_at else None,'duration_ms':t.duration_ms}
def _persist(db:Session,payload:AIExecuteRequest,t,user_id:str,fid:str|None,eid:str|None):
 AITaskService.upsert_runtime(t);AITaskService(db).persist_execution(t,operator_id=user_id,entity_id=payload.entity_id);a=AuditService(db);a.persist_event(a.build_event(module_name='ai',action_name='orchestrate_completed',operator_id=user_id,target_type='ai_task',target_id=t.task_id,result=t.status,detail={'scene':t.scene,'provider':t.provider,'duration_ms':t.duration_ms,'degraded':t.degraded,'error_message':t.error_message}))
 if payload.scene=='lead_followup' and payload.entity_id:
  a.persist_event(a.build_event(module_name='lead',action_name='ai_writeback',operator_id=user_id,target_type='lead',target_id=payload.entity_id,result=t.status,detail=t.context.get('writeback',{})))
  if fid:a.persist_event(a.build_event(module_name='lead',action_name='ai_generate_followup',operator_id=user_id,target_type='followup',target_id=fid,result=t.status,detail={'lead_id':payload.entity_id,'task_id':t.task_id}))
 if payload.scene=='proposal_generation' and payload.entity_id:a.persist_event(a.build_event(module_name='proposal',action_name='ai_writeback',operator_id=user_id,target_type='proposal',target_id=payload.entity_id,result=t.status,detail=t.context.get('writeback',{})))
 if payload.scene=='supplier_assessment' and payload.entity_id:
  a.persist_event(a.build_event(module_name='supplier',action_name='ai_writeback',operator_id=user_id,target_type='supplier',target_id=payload.entity_id,result=t.status,detail=t.context.get('writeback',{})))
  if eid:a.persist_event(a.build_event(module_name='supplier',action_name='ai_generate_evaluation',operator_id=user_id,target_type='supplier_evaluation',target_id=eid,result=t.status,detail={'supplier_id':payload.entity_id,'task_id':t.task_id}))
def _execute(payload:AIExecuteRequest,db:Session,user_id:str,task=None):
 t=task or service.prepare_task(scene=payload.scene,entity_id=payload.entity_id,context=payload.context);t=service.execute_task(task=t,entity_id=payload.entity_id,context=_kg(db,payload.scene,payload.context));fid=None;eid=None
 if payload.scene=='lead_followup' and payload.entity_id:
  lead=db.query(Lead).filter(Lead.id==payload.entity_id).first();
  if not lead:raise AppError(code='LEAD_NOT_FOUND',message='线索不存在，无法写回 AI 结果',status_code=404)
  c=max((float(i.get('confidence',0)) for i in t.insights),default=0.0);lead.ai_profile_summary=t.summary;lead.ai_next_action=t.next_actions[0] if t.next_actions else (t.recommendations[0] if t.recommendations else lead.ai_next_action);lead.ai_confidence=c;lead.ai_lead_score=round(c*100,2);lead.ai_risk_flag=json.dumps(t.evidence,ensure_ascii=False);lead.ai_priority_level,lead.ai_maturity_level=('P1','high') if lead.ai_lead_score>=85 else ('P2','medium') if lead.ai_lead_score>=60 else ('P3','low');lead.lead_status=_lead_status(lead.ai_lead_score,lead.ai_maturity_level,lead.lead_status);lead.crm_sync_status='ready';f=FollowupRecord(lead_id=lead.id,followup_type='ai_analysis',followup_channel='system',followup_content=t.summary,followup_result=lead.lead_status,next_action=lead.ai_next_action,recorder_user_id=user_id,ai_generated_flag=True);db.add(f);db.flush();fid=f.id;t.context['writeback']={'lead_id':lead.id,'ai_lead_score':lead.ai_lead_score,'ai_priority_level':lead.ai_priority_level,'ai_maturity_level':lead.ai_maturity_level,'lead_status':lead.lead_status,'generated_followup_id':fid}
 if payload.scene=='proposal_generation' and payload.entity_id:
  p=db.query(ProposalProject).filter(ProposalProject.id==payload.entity_id).first();
  if not p:raise AppError(code='PROPOSAL_NOT_FOUND',message='方案项目不存在，无法写回 AI 结果',status_code=404)
  p.generated_outline_uri=_outline(t);p.technical_draft_uri=_tech(t);p.commercial_draft_uri=_biz(t);p.version_no=int(p.version_no or 1)+1;p.proposal_status='generated';p.risk_level='high' if any('风险' in i for i in t.evidence) else p.risk_level;t.context['writeback']={'proposal_id':p.id,'version_no':p.version_no,'proposal_status':p.proposal_status,'generated_outline_written':bool(p.generated_outline_uri),'technical_draft_written':bool(p.technical_draft_uri),'commercial_draft_written':bool(p.commercial_draft_uri)}
 if payload.scene=='supplier_assessment' and payload.entity_id:
  s=db.query(Supplier).filter(Supplier.id==payload.entity_id).first();
  if not s:raise AppError(code='SUPPLIER_NOT_FOUND',message='供应商不存在，无法写回 AI 结果',status_code=404)
  c=max((float(i.get('confidence',0)) for i in t.insights),default=0.0);ts=round(c*100,2);r=_risk(c);sg=t.recommendations[0] if t.recommendations else t.summary;e=SupplierEvaluation(supplier_id=s.id,evaluation_period='AI即时评估',price_score=_score(c,88,76,62),delivery_score=_score(c,90,78,64),quality_score=_score(c,91,80,66),service_score=_score(c,89,79,65),risk_score=_score(c,86,74,60),qualification_score=_score(c,90,79,67),strategic_score=_score(c,87,75,61),total_score=ts,risk_level=r,cooperation_suggestion=sg,reviewer_user_id=user_id);db.add(e);db.flush();eid=e.id;s.supplier_status='active' if r=='low' else 'suspended' if r=='high' and s.supplier_status=='active' else s.supplier_status;t.context['writeback']={'supplier_id':s.id,'supplier_status':s.supplier_status,'generated_evaluation_id':eid,'total_score':ts,'risk_level':r,'cooperation_suggestion':sg}
 if payload.scene=='procurement_analysis':
  rfq=db.query(RFQ).filter(RFQ.id==payload.entity_id).first() if payload.entity_id else db.query(RFQ).order_by(RFQ.updated_at.desc()).first();
  if not rfq:raise AppError(code='RFQ_NOT_FOUND',message='当前没有可写回的询价任务',status_code=404)
  quotes=db.query(Quote).filter(Quote.rfq_id==rfq.id).order_by(Quote.quote_total_amount_tax.asc()).all();c=max((float(i.get('confidence',0)) for i in t.insights),default=0.0);rq=quotes[0] if quotes else None;rec={'ai_summary':t.summary,'recommended_supplier_id':rq.supplier_id if rq else '','recommended_quote_id':rq.id if rq else '','recommended_amount_tax':rq.quote_total_amount_tax if rq else 0,'risk_level':_risk(c),'recommendations':t.recommendations[:3],'evidence':t.evidence[:3],'next_actions':t.next_actions[:3],'knowledge_sources':t.context.get('knowledge_sources',[])};rfq.structured_requirement_json=json.dumps(rec,ensure_ascii=False);rfq.rfq_status='evaluating' if rfq.rfq_status in {'draft','published'} else rfq.rfq_status;pr=db.query(PurchaseRequest).filter(PurchaseRequest.id==rfq.pr_id).first();
  if pr and pr.request_status in {'draft','submitted','approved','sourcing'}:pr.request_status='sourcing'
  t.context['writeback']={'rfq_id':rfq.id,'rfq_status':rfq.rfq_status,'purchase_request_id':rfq.pr_id,'recommended_supplier_id':rec['recommended_supplier_id'],'recommended_quote_id':rec['recommended_quote_id'],'risk_level':rec['risk_level']}
 _persist(db,payload,t,user_id,fid,eid);db.commit();return t
def _run_async(payload:AIExecuteRequest,user_id:str,task_id:str):
 db=SessionLocal()
 try:
  t=service.prepare_task(scene=payload.scene,entity_id=payload.entity_id,context=payload.context);t.task_id=task_id;t.context={'entity_id':payload.entity_id,**_kg(db,payload.scene,payload.context)};t.status='running';AITaskService.upsert_runtime(t);_execute(payload,db,user_id,t)
 except Exception as exc:
  db.rollback();traceback.print_exc();t=service.prepare_task(scene=payload.scene,entity_id=payload.entity_id,context=payload.context);t.task_id=task_id;t.status='failed';t.error_message=str(exc);t.raw_output={'error':str(exc),'traceback':traceback.format_exc()};AITaskService.upsert_runtime(t);AITaskService(db).persist_execution(t,operator_id=user_id,entity_id=payload.entity_id);db.commit()
 finally:
  db.close()
@router.post('/orchestrate',response_model=APIResponse)
def orchestrate(payload:AIExecuteRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:return APIResponse(data=_resp(_execute(payload,db,current_user.id)))
@router.post('/tasks',response_model=APIResponse)
def create_task(payload:AIExecuteRequest,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
 t=service.prepare_task(scene=payload.scene,entity_id=payload.entity_id,context=payload.context);t.context={'entity_id':payload.entity_id,**_kg(db,payload.scene,payload.context)};AITaskService.upsert_runtime(t);a=AuditService(db);a.persist_event(a.build_event(module_name='ai',action_name='task_created',operator_id=current_user.id,target_type='ai_task',target_id=t.task_id,result='queued',detail={'scene':t.scene,'provider':t.provider}));db.commit();Thread(target=_run_async,args=(payload,current_user.id,t.task_id),daemon=True).start();return APIResponse(data=_resp(t))
@router.get('/tasks/{task_id}',response_model=APIResponse)
def task_status(task_id:str,db:Session=Depends(get_db),_:User=Depends(get_current_user))->APIResponse:
 r=AITaskService.get_runtime(task_id)
 if r:return APIResponse(data=r)
 i=AITaskService(db).get_execution(task_id)
 if not i:raise AppError(code='AI_TASK_NOT_FOUND',message='AI 执行任务不存在',status_code=404)
 ro=json.loads(i.raw_output) if i.raw_output else {}
 return APIResponse(data={'task_id':i.task_id,'scene':i.scene,'agent_name':i.agent_name,'provider':i.provider,'status':i.status,'summary':i.summary,'recommendations':json.loads(i.recommendations),'evidence':json.loads(i.evidence),'insights':json.loads(i.insights),'next_actions':json.loads(i.next_actions),'raw_output':ro,'context':json.loads(i.context),'degraded':i.status=='degraded','error_message':ro.get('error',''),'created_at':i.created_at.isoformat() if i.created_at else None,'completed_at':i.updated_at.isoformat() if i.updated_at else None,'duration_ms':0})
@router.get('/history',response_model=APIResponse)
def history(db:Session=Depends(get_db),_:User=Depends(get_current_user))->APIResponse:
 items=AITaskService(db).list_executions();return APIResponse(data=[{'task_id':i.task_id,'scene':i.scene,'agent_name':i.agent_name,'provider':i.provider,'operator_id':i.operator_id,'entity_id':i.entity_id,'status':i.status,'summary':i.summary,'created_at':i.created_at.isoformat() if i.created_at else None,'recommendations':json.loads(i.recommendations),'evidence':json.loads(i.evidence)} for i in items])
@router.get('/history/{task_id}',response_model=APIResponse)
def history_detail(task_id:str,db:Session=Depends(get_db),_:User=Depends(get_current_user))->APIResponse:
 i=AITaskService(db).get_execution(task_id)
 if not i:raise AppError(code='AI_TASK_NOT_FOUND',message='AI 执行记录不存在',status_code=404)
 return APIResponse(data={'task_id':i.task_id,'scene':i.scene,'agent_name':i.agent_name,'provider':i.provider,'operator_id':i.operator_id,'entity_id':i.entity_id,'status':i.status,'summary':i.summary,'created_at':i.created_at.isoformat() if i.created_at else None,'recommendations':json.loads(i.recommendations),'evidence':json.loads(i.evidence),'insights':json.loads(i.insights),'next_actions':json.loads(i.next_actions),'context':json.loads(i.context),'raw_output':json.loads(i.raw_output)})
