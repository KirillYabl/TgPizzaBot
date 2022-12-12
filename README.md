# Where to go

### Overview
The site is an interactive map with an expandable (in the admin panel) collection of places (for example, interesting places)
which have a title, description and a set of images.

[Working example](http://kirilliablunovskii.pythonanywhere.com/)

### How to install
Python3 should already be installed. Then use pip to install the dependencies ([virtual environment](https://docs.python.org/3/library/venv.html) is recommended):
```
pip install -r requirements.txt
```

You also need to update the database:
```
python manage.py migrate
```

Optionally (**You can run the site for yourself without this file**) create a `.env` file in `where_to_go` directory with the following options:
- `SECRET_KEY` - [secret key](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-SECRET_KEY) for you site
- `DEBUG` - boolean(true/false) parameter which turn on/off the debug mode. [More](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-DEBUG)
- `ALLOWED_HOSTS` - is a comma-separated list of IP addresses or URLs that the server can serve. [More](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts)

Sample contents of `.env` file:
```
SECRET_KEY=5n$@&*)3%586*j=jshty#uak(oi%(%_1^-3xh#pkz+=0m#(4b6
DEBUG=true
ALLOWED_HOSTS=127.0.0.1
```

That's all, you can start the server! Your site will be running at `127.0.0.1:8000`.
```
python manage.py runserver
```

### How to load data
There is a file `init_places.txt` with links to place data.
To download the data, after successfully installing the application, you can enter the following command to download the initial 28 locations:
```
python manage.py load_place init_places.txt -f
```

`load_place` usage:
`python manage.py load_place [url_or_path] [-f] [-fu]`

Where `url_or_path` is a positional argument that is the URL of a single location file or a file with multiple URLs.

The command `load_place` has next options:
- `-f`, `--file` - enter this option if you want to download a file with many location URLs, otherwise the command will wait for a URL with location data
- `-fu`, `--force_update` - the command will update the location with the same title if you enter this option, otherwise the program will ask you

An example of a file that the `load_place` command is waiting for at the given URL:
```json
{
    "title": "Пещеры Сьяны",
    "imgs": [
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/79b03d3bcce2f1bc02c855e5acfa686a.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/41ffbb0a5e6dbacdcce2f2893e2d6901.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/917e3a2aad19fe91f6603e7b473d3df3.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/ebeab798b7664070cd4494aacc715ad6.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/c26a133a499711b24c6042d9f23a65f8.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/46db27e9ed578050985dc157321ceba5.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/226bec43fa0c3af5310f89505025f87b.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/95ccbeaec84e9e48ca00e781ec21f34e.jpg",
        "https://raw.githubusercontent.com/devmanorg/where-to-go-places/master/media/f1fca1ef4da1afd92699110dfc19e9a4.jpg"
    ],
    "description_short": "Сьяновские каменоломни — это подмосковная система искусственных пещер. Когда конкретно здесь начались разработки, неизвестно, но возникновение пещеры принято датировать XVII веком, а наиболее активная работа проводилась в Сьянах во второй половине XIX века.",
    "description_long": "<p>В пещерах добывали строительный материал для крепостей и храмов белокаменной Москвы. В советское время отсюда возили камень для укрепления взлётных полос, в войну здесь размещался госпиталь, а после — сейсмическая станция. В 1974 году входы в Сьяны засыпали (по официальной версии, там пропал ребенок). К этому времени система подземных ходов превышала 90 км.</p><p>Заново освоение пещер началось в 1988 году, когда группа московских студентов на свой страх и риск раскопала один из входов — «Кошачий лаз». К этому времени протяжённость заброшенной пещеры сократилась до 19 километров, но это всё ещё самая крупная подземная система Подмосковья. Сейчас Сьяны представляют собой исхоженные и оборудованные для различных целей гроты и лазы. Здесь есть свой православный храм с расписанными стенами, концертная площадка и что-то вроде хостела — помещения со стульями и спальными местами.</p><p>Постоянные посетители Сьян именуют себя «системщиками», по примеру некогда могучего движения советских хиппи. Вокруг пещеры сложилась своя субкультура с традициями, правилами, мифами и ритуалами. Каждое второе воскресенье сентября «системщики» празднуют открытие нового сезона. Новичков приводят на аудиенцию к хранителю пещер — Аристарху, представляющему из себя старый комбинезон с прикрёпленным к нему человеческим черепом. Хранителя принято задабривать подарками, чтобы заручиться его помощью в подземных скитаниях. В качестве посвящения «юным сьяновцам» предлагают протиснуться через самые узкие лазы (Щучка и Карман). Так что лучше не наедаться перед спуском, чтобы не оказаться в положении Винни-Пуха, который пошёл в гости, а попал в безвыходное положение.</p><p>В пещере держится постоянная температура — +10°C, поэтому, отправляясь туда, одевайтесь тепло и не парадно. Перед тем, как решите посетить Сьяны, обязательно позаботьтесь о хорошем проводнике. Благо сейчас найти его не проблема, на разных сайтах и группах ВКонтакте вариантов экскурсий множество. Важно, чтобы ваш гид не только ориентировался в подземельях, но и был хорошим рассказчиком, потому что у «системщиков» есть много интересных легенд. Самые популярные из них — о Белом спелеологе и таинственной Двуликой, которая иногда выручает из беды хороших людей, а иногда заманивает их в ловушки.</p><p>Побывать в Сьянах — интересное приключение. Здесь легко дышится, несмотря на высокую влажность, но будьте готовы к тому, что в пещерах может оказаться много людей совершенно разного контингента. Также следует соблюдать технику безопасности при посещении каменоломен: на вынимать камни из бута и свода. Обязательно возьмите с собой в поход два фонарика (основной и запасной), а также запас еды и воды на всякий случай. Перед походом сообщите своим близким, куда вы отправились. В самой пещере отметьтесь в журнале о входе и выходе.</p><p>Добраться до пещер Сьяны можно от станции метро «Домодедовская», сев на любой автобус, идущий до посёлка Ленинские горки.</p>",
    "coordinates": {
        "lng": "37.797137",
        "lat": "55.480924"
    }
}
```

### How to use admin part of site
Stop the server if it is running.

Create a superuser and follow the command instructions
```
python manage.py createsuperuser
```

Start the server and navigate to `127.0.0.1:8000/admin`.

Enter the login and password that you created earlier while creating the superuser and that's it!

### Features
#### Place pictures
The first image will be displayed permanently and the rest of the images will be displayed on the slider bar.
You can set the image order in the site admin when adding a new location.

#### [WYSIWYG editor](https://en.wikipedia.org/wiki/WYSIWYG)
A long description of a place can be easily customized in the site admin using the WYSIWYG editor.

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
