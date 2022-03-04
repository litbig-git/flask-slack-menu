import datetime


class Block:
    def get_divider(self):
        _json = list()
        _json.append(
            {
                "type": "divider"
            }
        )
        return _json

    def get_header(self, date: datetime, comment: str):
        _json = list()
        _json.append(
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": comment
                }
            }
        )
        _json.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "*{eng_date}*  |  판교세븐벤처밸리".format(eng_date=date.strftime("%B %d, %Y"))
                    }
                ]
            }
        )
        return _json

    def get_menu(self, icon: str, when: str, menu: str = None):
        _json = list()
        _json.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":{icon}:  *{when}*".format(icon=icon, when=when)
                }
            }
        )
        if menu:
            _json.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "{menu}".format(menu=menu.replace('\n', ', '))
                    }
                }
            )
        return _json
