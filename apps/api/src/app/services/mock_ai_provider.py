from app.services.ai_provider import AIProvider, ProviderRequest, ProviderResult


class MockAIProvider(AIProvider):
    provider_name = "mock"

    def _text(self, value: object, fallback: str) -> str:
        text = str(value).strip() if value is not None else ""
        return text or fallback

    def execute(self, request: ProviderRequest) -> ProviderResult:
        context = request.context or {}
        scene = request.scene

        if scene == "lead_followup":
            company = self._text(context.get("company_name"), "当前客户")
            industry = self._text(context.get("industry_name"), "目标行业")
            priority = self._text(context.get("priority"), "普通优先级")
            return ProviderResult(
                summary=f"已结合{company}在线索阶段中的上下文信息，判断其在{industry}场景下具备继续推进价值，当前建议按{priority}节奏跟进。",
                recommendations=[f"优先联系{company}的关键决策人，确认预算与时间表", f"结合{industry}案例输出更贴近业务场景的沟通材料", "在 48 小时内形成一次可落地的需求澄清安排"],
                evidence=[f"当前对象为{company}，不是匿名线索", f"行业信息显示其属于{industry}，建议使用行业化话术", f"当前优先级为{priority}，说明已有推进价值"],
                next_actions=["整理下一次沟通提纲", "生成首轮拜访或电话话术", "同步客户管理系统并创建跟进任务"],
                insights=[{"title": "推进判断", "content": f"{company} 具备继续推进空间，关键在于尽快确认真实需求与决策链。", "confidence": 0.87}],
                raw_output={"scene": scene, "context_used": list(context.keys())},
            )

        if scene == "proposal_generation":
            project = self._text(context.get("project_name"), "当前项目")
            bid_type = self._text(context.get("bid_type"), "招采项目")
            risk = self._text(context.get("risk_level"), "medium")
            return ProviderResult(
                summary=f"已围绕{project}的{bid_type}特征生成方案建议，当前最需要优先处理的是风险等级为{risk}的约束项。",
                recommendations=["先整理技术方案目录并映射招标评分点", f"针对{risk}风险条款补一轮澄清问题清单", f"围绕{project}补充相似案例与交付计划"],
                evidence=[f"项目名称为{project}，方案内容应围绕该项目组织", f"当前招采类型为{bid_type}，需要匹配相应响应结构", f"风险等级为{risk}，应优先处理高风险条款"],
                next_actions=["输出方案大纲初稿", "补技术实施路径", "补商务应答与风险澄清"],
                insights=[{"title": "编制重点", "content": f"{project} 当前更适合先做结构化拆解，再进入技术和商务双线编制。", "confidence": 0.82}],
                raw_output={"scene": scene, "context_used": list(context.keys())},
            )

        if scene == "supplier_assessment":
            name = self._text(context.get("supplier_name"), "当前供应商")
            category = self._text(context.get("supplier_category"), "通用类")
            level = self._text(context.get("qualification_level"), "标准")
            status = self._text(context.get("supplier_status"), "active")
            return ProviderResult(
                summary=f"已对{name}完成初步评估，该供应商属于{category}，资质等级为{level}，当前状态为{status}，建议继续保留但增加风险复核。",
                recommendations=[f"围绕{name}补一次交付稳定性复核", "核验近 12 个月同类项目履约表现", "将付款与整改要求纳入后续合作条件"],
                evidence=[f"供应商名称为{name}，当前评估不是通用模板", f"分类为{category}，决定了合作关注点", f"资质等级为{level}、状态为{status}，需要结合治理策略判断"],
                next_actions=["发起季度复评", "补充风险标签", "输出合作建议摘要"],
                insights=[{"title": "合作建议", "content": f"{name} 可继续合作，但建议先确认履约与整改能力后再扩大份额。", "confidence": 0.8}],
                raw_output={"scene": scene, "context_used": list(context.keys())},
            )

        if scene == "procurement_analysis":
            request_count = self._text(context.get("purchase_request_count"), "0")
            quote_count = self._text(context.get("quote_count"), "0")
            return ProviderResult(
                summary=f"已结合当前{request_count}条采购需求和{quote_count}条报价记录生成采购建议，重点应放在价格与交付稳定性的平衡上。",
                recommendations=["优先锁定综合成本更优且交付更稳定的候选方", "对付款条件偏紧的报价发起二轮谈判", "在定标前补一次风险条款确认"],
                evidence=[f"当前采购需求数为{request_count}，说明存在持续采购背景", f"当前报价数为{quote_count}，已具备基础比价条件", "采购判断不应只看最低价，还要看账期与交付风险"],
                next_actions=["输出推荐供应商结论", "发起二轮议价", "准备内部审批材料"],
                insights=[{"title": "采购判断", "content": "建议优先选择成本、交付和风险表现更均衡的供应商。", "confidence": 0.81}],
                raw_output={"scene": scene, "context_used": list(context.keys())},
            )

        return ProviderResult(
            summary="已结合当前运营上下文输出 AI 运行质量与优化建议。",
            recommendations=["优先优化高频场景的提示词质量", "将降级场景单独监控", "补充人工反馈闭环"],
            evidence=[f"当前场景为{scene}", f"上下文字段数为{len(context)}", "需要持续观察模型质量、成本和采纳率"],
            next_actions=["复盘高频调用场景", "分析降级原因", "发布下一版提示词"],
            insights=[{"title": "运营观察", "content": "当前最具价值的优化方向是让输出更贴近业务对象，而不是只保证能调用。", "confidence": 0.83}],
            raw_output={"scene": scene, "context_used": list(context.keys())},
        )
