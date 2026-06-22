"""Group Topics 路由 — 每 Agent 一個 Topic。"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

log = logging.getLogger("topics")


@dataclass
class TopicConfig:
    """Group Topics 設定。"""
    group_id: int = 0
    agent_topics: dict[str, int] = field(default_factory=dict)  # agent_name → topic_id
    general_topic_id: int = 1
    alerts_topic_id: int | None = None
    daily_report_topic_id: int | None = None


class TopicRouter:
    """根據 agent 名稱路由訊息到對應 Topic。"""

    def __init__(self, config: TopicConfig):
        self.config = config

    @property
    def enabled(self) -> bool:
        return self.config.group_id != 0

    def get_topic_for_agent(self, agent_name: str) -> int | None:
        """取得 Agent 對應的 topic_id。"""
        return self.config.agent_topics.get(agent_name, self.config.general_topic_id)

    def get_alert_topic(self) -> int | None:
        return self.config.alerts_topic_id or self.config.general_topic_id

    def get_daily_report_topic(self) -> int | None:
        return self.config.daily_report_topic_id or self.config.general_topic_id

    async def send_to_agent_topic(self, bot, agent_name: str, text: str, parse_mode: str = "HTML") -> None:
        """發送訊息到 Agent 對應的 Topic。"""
        if not self.enabled:
            return
        topic_id = self.get_topic_for_agent(agent_name)
        try:
            await bot.send_message(
                chat_id=self.config.group_id,
                message_thread_id=topic_id,
                text=text,
                parse_mode=parse_mode,
            )
        except Exception as e:
            log.warning("Topic send failed (agent=%s, topic=%s): %s", agent_name, topic_id, e)

    async def send_alert(self, bot, text: str) -> None:
        """發送到 Alerts Topic。"""
        if not self.enabled:
            return
        topic_id = self.get_alert_topic()
        try:
            await bot.send_message(
                chat_id=self.config.group_id,
                message_thread_id=topic_id,
                text=text,
                parse_mode="HTML",
            )
        except Exception as e:
            log.warning("Alert send failed: %s", e)

    async def send_daily_report(self, bot, text: str) -> None:
        """發送到 Daily Report Topic。"""
        if not self.enabled:
            return
        topic_id = self.get_daily_report_topic()
        try:
            await bot.send_message(
                chat_id=self.config.group_id,
                message_thread_id=topic_id,
                text=text,
                parse_mode="HTML",
            )
        except Exception as e:
            log.warning("Daily report send failed: %s", e)

    @classmethod
    def from_team_yaml(cls, channel_config: dict) -> "TopicRouter":
        """從 team.yaml 的 channel 區塊建立。"""
        group_id = channel_config.get("group_id", 0)
        topics = channel_config.get("topics", {})
        # topics 格式: {topic_name: topic_id}，需轉換
        agent_topics = {}
        alerts_topic = None
        daily_topic = None
        general_topic = channel_config.get("general_topic_id", 1)

        for key, tid in topics.items():
            if "alert" in key.lower():
                alerts_topic = tid
            elif "daily" in key.lower() or "report" in key.lower():
                daily_topic = tid
            else:
                # 假設 topic 名稱含 agent 名
                agent_topics[key] = tid

        return cls(TopicConfig(
            group_id=group_id,
            agent_topics=agent_topics,
            general_topic_id=general_topic,
            alerts_topic_id=alerts_topic,
            daily_report_topic_id=daily_topic,
        ))
