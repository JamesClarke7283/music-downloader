# https://packaging.python.org/en/latest/tutorials/packaging-projects/
cd ../src
cp ../README.md README.md

echo "building......"
python3 -m pip install --upgrade build
python3 -m build

echo "cleaning up......."
rm README.md
cd ../build
rm -rf dist
mv ../src/dist .

echo "uploading......."
# python3 -m pip install --upgrade twine
twine upload dist/*
