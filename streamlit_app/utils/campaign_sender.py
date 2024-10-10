import asyncio
from telegram_ai_agent import TelegramAIAgent
from streamlit_app.utils.database.campaigns import update_recipient_status
from streamlit_app.utils.agent_factory import create_telegram_ai_agent


class CampaignSender:
    def __init__(self, agent: TelegramAIAgent, logger):
        self.agent = agent
        self.logger = logger

    async def send_campaign(self, campaign, recipients):
        await self.agent.start()
        try:
            for i, recipient in enumerate(recipients):
                try:
                    message = campaign.message_template
                    if campaign.make_unique:
                        message = await self.make_message_unique(message)

                    # Try to send message using username first, then phone number, then user_id
                    recipient_identifier = recipient.username or recipient.phone
                    if not recipient_identifier:
                        raise ValueError("No valid identifier found for recipient")

                    await self.agent.send_messages(
                        [recipient_identifier], message, throttle=campaign.throttle
                    )
                    update_recipient_status(campaign.id, recipient.user_id, "Sent")
                    yield i + 1, len(recipients), "Sent"
                except Exception as e:
                    self.logger.error(
                        f"Error processing recipient {recipient.user_id}: {str(e)}"
                    )
                    update_recipient_status(campaign.id, recipient.user_id, "Failed")
                    yield i + 1, len(recipients), f"Failed ({str(e)})"
        finally:
            await self.agent.stop()

    async def make_message_unique(self, message_template):
        prompt = f"Make the following message unique while preserving its main content and intent:\n\n{message_template}"
        response = self.agent.assistant.run(
            messages=[{"role": "user", "content": prompt}], stream=False
        )
        return str(response)


async def send_campaign(campaign, recipients, assistant_data, logger):
    agent = await create_telegram_ai_agent(assistant_data, logger)
    sender = CampaignSender(agent, logger)
    async for sent, total, status in sender.send_campaign(campaign, recipients):
        yield sent, total, status


def run_send_campaign(campaign, recipients, assistant_data, logger):
    async def run():
        results = []
        async for result in send_campaign(campaign, recipients, assistant_data, logger):
            results.append(result)
        return results

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(run())
