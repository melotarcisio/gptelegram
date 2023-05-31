support_email = ""

INITIAL_MESSAGE = (
    "Bem Vindo ao GPTelegram!\n"
    "Envie me qualquer mensagem e eu tentarei te ajudar."
    f"\n\nQualquer dúvida basta chamar o suporte pelo email: {support_email}"
)


LIMIT_EXCEEDED_MESSAGE = (
    "O GPTelegram utiliza o serviço da openai GPT-4 para gerar respostas."
    "A GPT-4 é um modelo de linguagem muito poderoso, porém é um serviço pago"
    "e para que eu seja sustentável, preciso cobrar por isso.\n"
    "A GPT é cobrada por uso e esse uso é medido em tokens, todos os novos usuários"
    "ganham 3000 tokens gratuitos para utilizar, como você atingiu esse limite, será necessário"
    "comprar mais tokens para continuar utilizando o serviço.\n"
    "Cada 1000 tokens custam R$ 0,25, você pode comprar quantos tokens quiser"
    "basta enviar uma mensagem no seguinte formato:\n/recarregar <quantidade de tokens>\n"
    "e você receberá um link para pagamento do mercado pago que é uma plataforma segura.\n"
    "\nPor exemplo, caso queira recarregar 5000 tokens, envie:\n"
    "/recarregar 5000\nAssim você receberá um link de pagamento no valor de R$ 1,25\n"
    "No momento em que o pagamento cair eu vou te avisar e você já poderá continuar usando o serviço.\n"
    f"\n\nQualquer dúvida basta chamar o suporte pelo email: {support_email}"
)


PAYMENT_OPTIONS_MESSAGE = (
    "para recarregar seus tokens, basta enviar uma mensagem no seguinte formato:\n"
    "/recarregar <quantidade de tokens>\n"
    "e você receberá um link para pagamento do mercado pago que é uma plataforma segura.\n"
    "\nPor exemplo, caso queira recarregar 5000 tokens, envie:\n"
    "/recarregar 5000\nAssim você receberá um link de pagamento no valor de R$ 1,25\n"
    "No momento em que o pagamento cair eu vou te avisar e você já poderá continuar usando o serviço."
    f"\n\nQualquer dúvida basta chamar o suporte pelo email: {support_email}"
)