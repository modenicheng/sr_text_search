import json
from tqdm import tqdm
from models import *


def update_db():
    with open(file='SR_Talk_CH.json', encoding='utf-8', mode='r') as f:
        data = json.load(f)

    with Session(engine) as session:
        for item in tqdm(data):
            new = Dialog(idx=item["I"], speaker=item['S'], text=item["T"])
            session.add(new)
            try:
                session.commit()
            except Exception as e:
                print(e)
                session.rollback()


if __name__ == '__main__':
    update_db()
