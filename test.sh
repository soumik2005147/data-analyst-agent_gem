#curl -X POST "http://127.0.0.1:8000/api/" -F "file=@question.txt"

#curl -F "file=@questions.txt" http://127.0.0.1:8000/api/

curl "http://127.0.0.1:8000/api/" -F "questions.txt=@question.txt"

#curl "http://127.0.0.1:8000/api/" -F "questions.txt=@question.txt" -F "data.csv=@data.csv"