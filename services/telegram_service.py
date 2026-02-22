"""Telegram Bot service wrapper.

Commands:
    /scan             - Trigger job alert scan.
    /approve <job_id> - Approve a pending outreach decision.
    /skip <job_id>    - Skip a pending outreach decision.
    /status           - List all pending decisions.

No business logic. All commands delegate to callback functions
registered via set_handlers().

Setup:
    1. Create a bot via @BotFather on Telegram.
    2. Set the TELEGRAM_BOT_TOKEN environment variable.
    3. Register callback functions via set_handlers() before calling run().
"""

import asyncio
import logging
from typing import Callable, Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from models import OutreachDecision

logger = logging.getLogger(__name__)


def format_decision(job_id: str, decision: OutreachDecision) -> str:
    """Format an OutreachDecision for Telegram display."""
    lines = [
        f"--- Job [{job_id}] ---",
        f"Title:   {decision.job.title}",
        f"Company: {decision.job.company}",
        f"Score:   {decision.match_score}",
        f"Contact: {decision.contact.status.value}",
        f"Action:  {decision.action.value}",
    ]
    if decision.reason:
        lines.append(f"Reason:  {decision.reason}")
    if decision.contact.recruiter_email:
        lines.append(f"Email:   {decision.contact.recruiter_email}")
    if decision.action.value == "READY_TO_SEND":
        lines.append(f"\n/approve {job_id}  or  /skip {job_id}")
    return "\n".join(lines)


class TelegramBot:
    """Thin Telegram bot wrapper. Routes commands to external callbacks.

    Callbacks (registered via set_handlers):
        on_scan:    () -> str
        on_approve: (job_id: str, decision: OutreachDecision) -> str
        on_skip:    (job_id: str, decision: OutreachDecision) -> str
        on_status:  (pending: dict[str, OutreachDecision]) -> str

    All callbacks are synchronous functions executed in a thread pool
    to avoid blocking the event loop.
    """

    def __init__(self, token: str):
        self._app: Application = Application.builder().token(token).build()
        self._pending: dict[str, OutreachDecision] = {}
        self._on_scan: Optional[Callable[[], str]] = None
        self._on_approve: Optional[Callable[[str, OutreachDecision], str]] = None
        self._on_skip: Optional[Callable[[str, OutreachDecision], str]] = None
        self._on_status: Optional[Callable[[dict[str, OutreachDecision]], str]] = None

        self._app.add_handler(CommandHandler("scan", self._handle_scan))
        self._app.add_handler(CommandHandler("approve", self._handle_approve))
        self._app.add_handler(CommandHandler("skip", self._handle_skip))
        self._app.add_handler(CommandHandler("status", self._handle_status))

    def set_handlers(
        self,
        on_scan: Callable[[], str],
        on_approve: Callable[[str, OutreachDecision], str],
        on_skip: Callable[[str, OutreachDecision], str],
        on_status: Callable[[dict[str, OutreachDecision]], str],
    ) -> None:
        """Register command callbacks. Must be called before run()."""
        self._on_scan = on_scan
        self._on_approve = on_approve
        self._on_skip = on_skip
        self._on_status = on_status

    @property
    def pending(self) -> dict[str, OutreachDecision]:
        """Return a copy of current pending decisions."""
        return dict(self._pending)

    def add_pending(self, job_id: str, decision: OutreachDecision) -> None:
        """Store a decision for later /approve or /skip."""
        self._pending[job_id] = decision

    async def send_message(self, chat_id: int, text: str) -> None:
        """Send a text message to a specific chat."""
        await self._app.bot.send_message(chat_id=chat_id, text=text)

    async def _handle_scan(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self._on_scan:
            await update.message.reply_text("Scan handler not configured.")
            return
        try:
            result = await asyncio.to_thread(self._on_scan)
        except Exception:
            logger.exception("/scan handler failed")
            await update.message.reply_text("Scan failed. Check logs.")
            return
        await update.message.reply_text(result)

    async def _handle_approve(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self._on_approve:
            await update.message.reply_text("Approve handler not configured.")
            return
        if not context.args:
            await update.message.reply_text("Usage: /approve <job_id>")
            return
        job_id = context.args[0]
        decision = self._pending.pop(job_id, None)
        if not decision:
            await update.message.reply_text(
                f"No pending decision for job_id: {job_id}"
            )
            return
        try:
            result = await asyncio.to_thread(self._on_approve, job_id, decision)
        except Exception:
            logger.exception("/approve handler failed for %s", job_id)
            self._pending[job_id] = decision
            await update.message.reply_text(
                f"Approve failed for [{job_id}]. Decision restored to pending."
            )
            return
        await update.message.reply_text(result)

    async def _handle_skip(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self._on_skip:
            await update.message.reply_text("Skip handler not configured.")
            return
        if not context.args:
            await update.message.reply_text("Usage: /skip <job_id>")
            return
        job_id = context.args[0]
        decision = self._pending.pop(job_id, None)
        if not decision:
            await update.message.reply_text(
                f"No pending decision for job_id: {job_id}"
            )
            return
        try:
            result = await asyncio.to_thread(self._on_skip, job_id, decision)
        except Exception:
            logger.exception("/skip handler failed for %s", job_id)
            self._pending[job_id] = decision
            await update.message.reply_text(
                f"Skip failed for [{job_id}]. Decision restored to pending."
            )
            return
        await update.message.reply_text(result)

    async def _handle_status(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self._on_status:
            await update.message.reply_text("Status handler not configured.")
            return
        try:
            result = await asyncio.to_thread(
                self._on_status, dict(self._pending)
            )
        except Exception:
            logger.exception("/status handler failed")
            await update.message.reply_text("Status check failed. Check logs.")
            return
        await update.message.reply_text(result)

    def run(self) -> None:
        """Start the bot polling loop. Blocks until stopped."""
        self._app.run_polling()
