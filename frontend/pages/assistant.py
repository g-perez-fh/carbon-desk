from datetime import date, timedelta

from fastapi.responses import RedirectResponse
from nicegui import ui

from frontend import api, session
from frontend.components import call_api, kg, section_title
from frontend.layout import page_layout

EFFORT_COLOURS = {"low": "positive", "medium": "warning", "high": "negative"}


@ui.page("/assistant")
async def page():
    if not session.token():
        return RedirectResponse("/login")

    with page_layout("AI Sustainability Assistant"):
        with ui.tabs().classes("w-full") as tabs:
            chat_tab = ui.tab("Chat")
            recommendations_tab = ui.tab("Recommendations")
            summaries_tab = ui.tab("Monthly summaries")
        with ui.tab_panels(tabs, value=chat_tab).classes("w-full"):
            with ui.tab_panel(chat_tab):
                chat = ChatPanel()
            with ui.tab_panel(recommendations_tab):
                recommendations_box = ui.column().classes("w-full gap-4")
            with ui.tab_panel(summaries_tab):
                summaries_box = ui.column().classes("w-full gap-4")

    await ui.context.client.connected()
    await chat.load_conversations()
    await recommendations_section(recommendations_box, date.today().year)
    await summaries_section(summaries_box)


# Chat ------------------------------------------------------------------------------


class ChatPanel:
    """Conversation list on the left, the selected conversation on the right."""

    def __init__(self):
        self.conversation_id = None
        with ui.row().classes("w-full no-wrap gap-4 items-stretch"):
            with ui.column().classes("w-60 shrink-0"):
                ui.button("New chat", icon="add", on_click=self.new_chat).classes("w-full")
                self.list_box = ui.column().classes("w-full gap-1")
            with ui.column().classes("grow"):
                self.messages = ui.scroll_area().classes("w-full h-[28rem] border rounded")
                with ui.row().classes("w-full items-center no-wrap"):
                    self.input = ui.input(placeholder="Ask about your emissions…").classes("grow")
                    self.input.on("keydown.enter", self.send)
                    self.send_button = ui.button(icon="send", on_click=self.send)
        self.show_welcome()

    def show_welcome(self):
        self.messages.clear()
        with self.messages:
            ui.markdown(
                "Ask questions about your company's emissions, for example:\n\n"
                "- *Where do most of our emissions come from?*\n"
                "- *How can we reduce Scope 2 emissions?*\n"
                "- *Are we on track for our targets?*"
            ).classes("text-gray-600 p-2")

    async def load_conversations(self):
        ok, conversations = await call_api(api.get("assistant/conversations/"))
        if not ok:
            return
        self.list_box.clear()
        with self.list_box:
            for conversation in conversations:
                selected = conversation["id"] == self.conversation_id
                with ui.row().classes("w-full items-center no-wrap"):
                    ui.button(
                        conversation["title"] or "New conversation",
                        on_click=lambda c=conversation["id"]: self.open(c),
                    ).props(
                        f"flat no-caps align=left {'' if selected else 'color=grey-8'}"
                    ).classes("grow truncate")
                    ui.button(
                        icon="delete", on_click=lambda c=conversation["id"]: self.remove(c)
                    ).props("flat round dense size=sm color=grey")

    async def open(self, conversation_id):
        ok, conversation = await call_api(api.get(f"assistant/conversations/{conversation_id}/"))
        if not ok:
            return
        self.conversation_id = conversation_id
        self.messages.clear()
        for message in conversation["messages"]:
            self.add_message(message)
        if not conversation["messages"]:
            self.show_welcome()
        await self.load_conversations()

    async def new_chat(self):
        self.conversation_id = None
        self.show_welcome()
        await self.load_conversations()

    async def remove(self, conversation_id):
        ok, _ = await call_api(api.delete(f"assistant/conversations/{conversation_id}/"))
        if ok and conversation_id == self.conversation_id:
            await self.new_chat()
        elif ok:
            await self.load_conversations()

    def add_message(self, message):
        is_user = message["role"] == "user"
        with self.messages:
            with ui.chat_message(name="You" if is_user else "CarbonDesk", sent=is_user):
                ui.markdown(message["content"])
        self.messages.scroll_to(percent=1.0)

    async def send(self):
        text = (self.input.value or "").strip()
        if not text:
            return
        if self.conversation_id is None:
            ok, conversation = await call_api(api.post("assistant/conversations/", json={}))
            if not ok:
                return
            self.conversation_id = conversation["id"]
            self.messages.clear()

        self.input.value = ""
        self.input.disable()
        self.send_button.disable()
        self.add_message({"role": "user", "content": text})
        with self.messages:
            thinking = ui.spinner("dots", size="lg")
        try:
            ok, reply = await call_api(
                api.post(
                    f"assistant/conversations/{self.conversation_id}/messages/",
                    json={"content": text},
                )
            )
        finally:
            thinking.delete()
            self.input.enable()
            self.send_button.enable()
        if ok:
            self.add_message(reply["answer"])
            await self.load_conversations()


# Recommendations ------------------------------------------------------------------


async def recommendations_section(box, year):
    ok, data = await call_api(api.get("assistant/recommendations/", params={"year": year}))
    if not ok:
        return
    box.clear()
    with box:
        with ui.row().classes("w-full items-center"):
            section_title("Reduction recommendations")
            ui.space()
            this_year = date.today().year
            ui.select(
                list(range(this_year, this_year - 5, -1)),
                value=year,
                label="Year",
                on_change=lambda e: recommendations_section(box, e.value),
            ).classes("w-28")

        with ui.row().classes("w-full"):
            for key, label in [
                ("scope_1", "Scope 1"),
                ("scope_2", "Scope 2"),
                ("scope_3", "Scope 3"),
            ]:
                with ui.card().classes("grow"):
                    ui.label(label).classes("text-gray-500")
                    ui.label(kg(data["totals"][key])).classes("text-lg font-medium")
            with ui.card().classes("grow bg-emerald-50"):
                ui.label("Total").classes("text-gray-500")
                ui.label(kg(data["total"])).classes("text-lg font-semibold")

        if not data["recommendations"]:
            ui.label(
                f"No emissions recorded for {year}. Add activity data on the Emissions page "
                "to get recommendations."
            ).classes("text-gray-500")
            return
        for rec in data["recommendations"]:
            with ui.card().classes("w-full"):
                with ui.row().classes("w-full items-center"):
                    ui.label(rec["title"]).classes("text-base font-medium")
                    ui.badge(f"Scope {rec['scope']}", color="teal")
                    ui.badge(f"{rec['effort']} effort", color=EFFORT_COLOURS[rec["effort"]])
                    ui.space()
                    ui.label(f"≈ {kg(rec['estimated_savings_kg_co2e'])} / year").classes(
                        "font-semibold text-emerald-800"
                    )
                ui.label(rec["description"]).classes("text-gray-600")
        ui.label(
            "Savings are indicative estimates based on typical reductions for small and "
            "medium companies."
        ).classes("text-xs text-gray-500")


# Monthly summaries -----------------------------------------------------------------


async def summaries_section(box):
    ok, summaries = await call_api(api.get("assistant/summaries/"))
    if not ok:
        return
    box.clear()
    with box:
        section_title("Monthly summaries")
        if session.can_edit():
            last_month = date.today().replace(day=1) - timedelta(days=1)
            with ui.row().classes("items-end"):
                month = ui.input("Month", value=f"{last_month:%Y-%m}").props("type=month")

                async def generate():
                    button.disable()
                    try:
                        ok, _ = await call_api(
                            api.post("assistant/summaries/", json={"month": month.value}),
                            "Summary generated",
                        )
                    finally:
                        button.enable()
                    if ok:
                        await summaries_section(box)

                button = ui.button("Generate summary", icon="summarize", on_click=generate)
        if not summaries:
            ui.label("No summaries generated yet.").classes("text-gray-500")
        for summary in summaries:
            title = date.fromisoformat(summary["month"]).strftime("%B %Y")
            with ui.expansion(title, icon="calendar_month").classes("w-full border rounded"):
                ui.markdown(summary["content"])
                ui.label(
                    f"Generated by {summary['generated_by'] or '—'} on {summary['updated_at'][:10]}"
                ).classes("text-xs text-gray-500")
