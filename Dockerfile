FROM python:3.7
ARG production=1
ENV SHOP_PRODUCTION 1
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "crowdrobot_alive_checker.py"]
CMD ["python", "rest_api/crowdbot_rest_api.py"]

