import json
from json import JSONDecodeError

import httpx

from app.core.config import get_settings
from app.services.ai_provider import AIProvider, AIProviderError, ProviderRequest, ProviderResult


class AliyunQwenProvider(AIProvider):
    provider_name = "aliyun_qwen"

    def _build_system_prompt(self, scene: str) -> str:
        prompts = {
            "lead_followup": "你是资深 B2B 销售教练。请基于客户画像、来源渠道、项目阶段、需求摘要、评分和下一步动作，输出更像销售经理会采用的推进判断。",
            "proposal_generation": "你是资深售前方案总监。请基于项目名称、招采类型、风险等级、审批状态、评分规则、方案版本和知识来源，输出结构化且可执行的编制建议。",
            "supplier_assessment": "你是供应商管理负责人。请基于供应商类别、资质、状态、区域、产品、结算条件、最近评估结果和知识来源，给出风险判断、治理动作和合作策略。",
            "procurement_analysis": "你是采购决策顾问。请基于采购需求规模、询价数量、报价情况、推荐供应商、决策依据和知识来源，分别输出比价建议、谈判建议和定标建议。",
            "ops_analysis": "你是企业 AI 运营分析师。请基于运行状态、质量、成本和异常信号，输出运营结论和优化建议。",
        }
        common = "请严格输出 JSON，不要输出 JSON 以外的任何文字。summary 必须点名至少 1 个上下文字段；recommendations、evidence、next_actions 必须具体可执行；insights 至少 1 条且 confidence 为 0 到 1 的小数。若 knowledge_sources 存在，evidence 中至少引用 1 个 doc_name。严禁空泛表述。"
        return f"{prompts.get(scene, prompts['ops_analysis'])}{common}"

    def _build_user_prompt(self, request: ProviderRequest) -> str:
        scene_requirements = {
            "lead_followup": "重点识别客户优先级、需求紧迫性、决策链与 48 小时内应推进的销售动作。",
            "proposal_generation": "重点输出方案结构、评分映射、风险条款、技术商务分工与版本推进建议。",
            "supplier_assessment": "重点输出履约风险、整改建议、合作范围控制与是否扩大合作份额。",
            "procurement_analysis": "recommendations 中至少覆盖 1 条比价建议、1 条谈判建议、1 条定标建议。",
            "ops_analysis": "重点输出异常信号、影响范围和可执行优化动作。",
        }
        return (
            f"scene={request.scene}\n"
            f"entity_id={request.entity_id}\n"
            f"context={json.dumps(request.context, ensure_ascii=False)}\n\n"
            "输出要求：\n"
            f"0. {scene_requirements.get(request.scene, '输出必须紧贴当前业务对象。')}\n"
            "1. summary 用一句话总结当前对象最值得关注的判断；\n"
            "2. recommendations 给 3 条建议，必须与当前上下文直接相关；\n"
            "3. evidence 给 2-4 条依据，必须体现你为何得出该判断；\n"
            "4. insights 至少 1 条，title 和 content 要业务化；\n"
            "5. next_actions 给 3 条下一步动作，尽量带时间性或执行对象；\n"
            "6. 避免泛泛而谈，如“建议持续优化”“建议加强沟通”；\n"
            "7. 若存在 knowledge_sources，必须在 evidence 或建议中明确引用文档名称。\n\n"
            "请严格返回如下 JSON 结构："
            '{"summary":"","recommendations":[],"evidence":[],"insights":[{"title":"","content":"","confidence":0.0}],"next_actions":[]}'
        )

    def _extract_json(self, content: str) -> dict:
        text = content.strip()
        try:
            return json.loads(text)
        except JSONDecodeError:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end + 1])
            raise AIProviderError("Aliyun Qwen returned non-JSON content", retryable=False, allow_fallback=False)

    def execute(self, request: ProviderRequest) -> ProviderResult:
        settings = get_settings()
        if not settings.ai_api_key:
            raise AIProviderError("Aliyun DashScope API key is missing", retryable=False, allow_fallback=False)
        if not settings.ai_base_url:
            raise AIProviderError("Aliyun DashScope base url is missing", retryable=False, allow_fallback=False)

        url = f"{settings.ai_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": settings.ai_model_name,
            "messages": [
                {"role": "system", "content": self._build_system_prompt(request.scene)},
                {"role": "user", "content": self._build_user_prompt(request)},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }

        timeout = max(settings.ai_timeout_seconds, 300)
        retries = min(settings.ai_retry_count, 1)
        last_exc: Exception | None = None

        for _ in range(retries + 1):
            try:
                response = httpx.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {settings.ai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = self._extract_json(content)
                return ProviderResult(
                    summary=parsed.get("summary", ""),
                    recommendations=parsed.get("recommendations", []),
                    evidence=parsed.get("evidence", []),
                    insights=parsed.get("insights", []),
                    next_actions=parsed.get("next_actions", []),
                    raw_output=data,
                )
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code in {400, 401, 403, 404}:
                    raise AIProviderError(f"Aliyun Qwen request rejected: HTTP {status_code}", retryable=False, allow_fallback=False) from exc
                last_exc = AIProviderError(f"Aliyun Qwen transient HTTP error: HTTP {status_code}", retryable=True, allow_fallback=False)
            except httpx.TimeoutException as exc:
                last_exc = AIProviderError("Aliyun Qwen request timed out", retryable=True, allow_fallback=False)
            except httpx.HTTPError as exc:
                last_exc = AIProviderError(f"Aliyun Qwen network error: {exc}", retryable=True, allow_fallback=False)
            except AIProviderError as exc:
                if not exc.retryable:
                    raise
                last_exc = exc
            except Exception as exc:
                raise AIProviderError(f"Unexpected Aliyun response: {exc}", retryable=False, allow_fallback=False) from exc

        raise AIProviderError(f"Aliyun Qwen request failed after retries: {last_exc}", retryable=False, allow_fallback=False) from last_exc
