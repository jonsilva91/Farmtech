import os
import boto3

def get_sns_client():
    return boto3.client(
        "sns",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

def enviar_alerta(mensagem: str, assunto: str = "Alerta FarmTech"):
    topic_arn = os.getenv("AWS_SNS_ARN")
    if not topic_arn:
        raise RuntimeError("AWS_SNS_ARN não configurado")

    client = get_sns_client()
    client.publish(
        TopicArn=topic_arn,
        Message=mensagem,
        Subject=assunto,
    )
