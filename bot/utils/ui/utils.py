async def disable_buttons(self):
    for child in self.children:
        child.disabled = True

    await self.interaction.edit_original_message(view=self)
