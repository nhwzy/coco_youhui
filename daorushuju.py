import pandas as pd
import os


def main():
    from blog.models import Location
    df = pd.read_excel('Coco都可茶饮.xls')
    coco_data = []
    for i in df.index.values:
        row_data = df.loc[i, ['x', 'y', 'count', 'name']].to_dict()
        coco_data.append(row_data)
    for i in coco_data:
        x=i['x']
        y=i['y']
        name=i['name']
        Location.objects.get_or_create(x=x,y=y,name=name)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoBlog.settings")
    import django
    django.setup()
    main()
    print('Done!')