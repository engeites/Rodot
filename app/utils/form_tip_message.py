from app.database.models import ParentingTip


class TipRenderer:
    def __init__(self, tip: ParentingTip):
        self.tip: ParentingTip = tip

    def form_tip_body(self):
        text = f"<b>{self.tip.header}</b> \n\n"
        text += self.tip.tip
        return text

    def add_advertisement(self):
        # search for advertisements according to tip.id
        # add advertisement text to bottom
        # return ad_text
        pass

    def render_tip(self):
        final_message_text = self.form_tip_body()
        # if self.tip.ad:
        #     self.add_advertisement()

        return final_message_text
