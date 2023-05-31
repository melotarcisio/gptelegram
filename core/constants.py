support_email = "melotarcisio@hotmail.com"

INITIAL_MESSAGE = (
    "Bem Vindo ao GPTelegram!\n"
    "Envie me qualquer mensagem e eu tentarei te ajudar."
    f"\n\nCaso tenha algum problema, entre em contato com o desenvolvedor: {support_email}"
)



PAYMENT_OPTIONS_MESSAGE = (
    "para recarregar seus tokens, basta enviar uma mensagem no seguinte formato:\n"
    "/recarregar <quantidade de tokens>\n"
    "e você receberá um link para pagamento do mercado pago que é uma plataforma segura.\n"
    "\nPor exemplo, caso queira recarregar 5000 tokens, envie:\n"
    "/recarregar 5000\nAssim você receberá um link de pagamento no valor de R$ 1,25\n"
    "No momento em que o pagamento cair eu vou te avisar e você já poderá continuar usando o serviço."
    f"\n\nCaso tenha algum problema, entre em contato com o desenvolvedor: {support_email}"
)


LIMIT_EXCEEDED_MESSAGE_FREE = (
    "O GPTelegram utiliza o serviço da openai GPT-4 para gerar respostas."
    "A GPT-4 é um modelo de linguagem muito poderoso, porém é um serviço pago"
    "e para que eu seja sustentável, preciso cobrar por isso.\n"
    "As nossas conversas consomem tokens, que são a moeda de troca da openai.\n"
    "Quando você se cadastrou, você recebeu 3000 tokens gratuitos para utilizar"
    " e os seus tokense se esgotaram em sua ultima mensagem.\n"
    f"{PAYMENT_OPTIONS_MESSAGE}"
)

LIMIT_EXCEEDED_MESSAGE_PAID = (
    "Seus tokens acabaram, mas você pode recarregar a qualquer momento.\n"
    f"{PAYMENT_OPTIONS_MESSAGE}"
)