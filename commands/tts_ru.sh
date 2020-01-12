#!/bin/bash
#Скачивает слово из гугла в mp3 формате
if [ -z "$1" ]
then
    echo "USAGE: ttc_ru.sh text_to_speach"
    exit 1
fi

WORD=$1

q=${WORD//\ /%20}
storage='/home/db/tts'
[ -d $storage ] || mkdir -p $storage
file="${q}.mp3"

if [ ! -f $storage/$file ]
then
    /usr/bin/curl -s "https://translate.google.com/translate_tts?ie=UTF-8&q=$q&tl=ru&client=tw-ob" -H 'Referer: http://translate.google.com/' -H 'User-Agent: stagefright/1.2 (Linux;Android 5.0)' > $storage/$file 
fi

/usr/bin/mpg123 -q $storage/$file
