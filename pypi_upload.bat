echo off
copy ..\ideas\ideas\token_utils.py token_utils\token_utils.py
git add *
git commit -m "Keeping version in sync with that of ideas"
git push
del /Q dist\*.*
python setup.py sdist bdist_wheel
twine upload dist/*
