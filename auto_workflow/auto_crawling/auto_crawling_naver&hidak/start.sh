mkdir ./dags
mkdir ./data_hidak
mkdir ./data_naver
git clone https://github.com/cheol2Y/Final_project_dags.git
mv ./Final_project_dags/*.py ./dags/

docker-compose up -d

# 볼륨을 공유하는 폴더의 권한을 변경하여 airflow 컨테이너 내부에서 수정 가능하게 한다.
chmod -R 777 ./data_hidak
chmod -R 777 ./data_naver

sudo chown -R 1000:1000 dags
sudo chown -R 1000:1000 data_naver
sudo chown -R 1000:1000 data_hidak

rm -rf ./Final_project_dags