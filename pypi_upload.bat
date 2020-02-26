echo off
cp ..\ideas\ideas\token_utils.py token_utils\token_utils.py
git add *
git commit -m "Keeping version in sync with that of ideas"
git push
:Ask
echo Did you update the version?(y/n)
set ANSWER=
set /P ANSWER=Type input: %=%
If /I "%ANSWER%"=="y" goto yes
If /I "%ANSWER%"=="n" goto no
echo Incorrect input & goto Ask
:yes
del /Q dist\*.*
python setup.py sdist bdist_wheel
twine upload dist/*
:no
