mkdir docs

set origin=%cd%
cd src
%origin%\venv\Scripts\python.exe -m pydoc -w %cd%
cd %origin%
