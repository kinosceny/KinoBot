create table users(
    "id" serial primary key,
    "telegram_id" bigint not null,
    "films" int[] not null,
    "created_timestamp" timestamp not null default (now() at time zone 'utc')
);

create table films(
    "id" serial primary key,
    "film_id" int not null,
    "path_to_video" text not null,
    "icon" text not null,
    "video_name" text not null,
    "film_name" text not null,
    "text" text not null,
    "link" text not null,
    "link_found" text not null,
    "link_text" text not null
);

create table bot_settings(
    "id" serial primary key,
    "start_message" text not null default 'Добро пожаловать в бота!
    
Для ввода кода нажмите на кнопку ниже 👇',
    "code_message" text not null default 'Введите код ниже',
    "after_link" text not null default 'Данный фильм также доступен Вам в разделе «⭐️ Мои фильмы»',
    "not_found_code_message" text not null default 'Не найдено',
    "film_cost" int not null default 50,
    "is_working" bool not null default True
);

INSERT INTO bot_settings DEFAULT VALUES;