import json 

class Shifts:
    def __init__(self, title, place, form_link, photo, about, dates, remark="") -> None:
        self.title = title
        self.place = place
        self.form_link = form_link
        self.photo = photo
        self.about = about
        self.dates = dates
        self.remark = remark

    def add_shift(self):
        with open("info.json", "r") as f:
            data = json.load(f)

        data["shifts"].append({
            "title": self.title,
            "place": self.place,
            "form_link": self.form_link,
            "photo": self.photo,
            "about": self.about,
            "dates": self.dates,
            "remark": self.remark
        })

        
        with open("info.json", "w") as f:
            json.dump(data)
