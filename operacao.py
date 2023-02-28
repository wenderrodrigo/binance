from datetime import datetime
import time
import decimal
# from datetime import datetime
# from datetime import timedelta
from decimal import Decimal
import math
from binance.client import Client

from pprint import pprint
# import telegram_send
import telegram
from pytz import timezone

import rf_signals

api_key_telagram = '1844067108:AAGC0PhpPk-0pwPf_PJUJls4tWKExFTqYYE'

SYMBOL_TYPE_SPOT = 'SPOT'

ORDER_STATUS_NEW = 'NEW'
ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
ORDER_STATUS_FILLED = 'FILLED'
ORDER_STATUS_CANCELED = 'CANCELED'
ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
ORDER_STATUS_REJECTED = 'REJECTED'
ORDER_STATUS_EXPIRED = 'EXPIRED'

KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'
KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'
KLINE_INTERVAL_1WEEK = '1w'
KLINE_INTERVAL_1MONTH = '1M'

SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'

ORDER_TYPE_LIMIT = 'LIMIT'
ORDER_TYPE_MARKET = 'MARKET'
ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

TIME_IN_FORCE_GTC = 'GTC'
TIME_IN_FORCE_IOC = 'IOC'
TIME_IN_FORCE_FOK = 'FOK'

ORDER_RESP_TYPE_ACK = 'ACK'
ORDER_RESP_TYPE_RESULT = 'RESULT'
ORDER_RESP_TYPE_FULL = 'FULL'

# For accessing the data returned by Client.aggregate_trades().
AGG_ID = 'a'
AGG_PRICE = 'p'
AGG_QUANTITY = 'q'
AGG_FIRST_TRADE_ID = 'f'
AGG_LAST_TRADE_ID = 'l'
AGG_TIME = 'T'
AGG_BUYER_MAKES = 'm'
AGG_BEST_MATCH = 'M'

api_key = 'Q4OyFb92b7TprAN1tOjX7kiFNVxo8TQraMgtTgDR9VCKAcKoEsnzxpzo8RpN6Q57'
api_secret = 'OvWrxJaxoctV1xYeG7K3iERjHPDATPOhw10Lnv9JnUlqU3ubQ6ejOp8vvvsz7BZk'

client = Client(api_key, api_secret)


def type_kendall(open, close):
    if open > close:
        return -1
    elif open < close:
        return 1
    else:
        return 0


def tamanho_kenddal(open, close):
    if type_kendall(open, close) == 1:
        return close - open
    else:
        return open - close


def busca(lista, valor):
    for el in lista:
        if valor == el['symbol']:
            return el

    return False


def seis_anteriores(candles, i, ttl):
    y = i - 6;
    x = i
    qtd_suporte = 0
    qtd_resistencia = 0
    while i > y:
        atual_open_kendall = Decimal(candles[ttl][1])
        atual_close_kendall = Decimal(candles[ttl][4])
        atual_tipo_kendall = type_kendall(atual_open_kendall, atual_close_kendall)

        if atual_tipo_kendall == 1:
            atual_suporte_kendall = atual_open_kendall
            atual_resistencia_kendall = atual_close_kendall
        else:
            atual_suporte_kendall = atual_close_kendall
            atual_resistencia_kendall = atual_open_kendall

        open_kendall = Decimal(candles[i][1])
        close_kendall = Decimal(candles[i][4])
        tipo_kendall = type_kendall(open_kendall, close_kendall)

        if tipo_kendall == 1:
            suporte_kendall = open_kendall
            resistencia_kendall = close_kendall
        else:
            suporte_kendall = close_kendall
            resistencia_kendall = open_kendall

        if atual_suporte_kendall > resistencia_kendall:
            qtd_suporte = qtd_suporte + 1

        if atual_resistencia_kendall < suporte_kendall:
            qtd_resistencia = qtd_resistencia + 1

        i = i - 1

    return qtd_suporte, qtd_resistencia, x


def suporte_resistencia(candles):
    limit = 400 if len(candles) >= 450 else 0
    i = len(candles) - 1
    t = i - 6
    ttl = i
    resistencia = 0
    suporte = 0

    while i > limit:

        # time_kendall = candles[i][0]
        open_kendall = Decimal(candles[i][1])
        max_kendall = Decimal(candles[i][2])
        min_kendall = Decimal(candles[i][3])
        close_kendall = Decimal(candles[i][4])
        tipo_kendall = type_kendall(open_kendall, close_kendall)

        if tipo_kendall == 1:
            suporte_kendall = open_kendall
            resistencia_kendall = close_kendall
        else:
            suporte_kendall = close_kendall
            resistencia_kendall = open_kendall

        if i == len(candles) - 1:
            # atual_time_kendall = time_kendall
            atual_open_kendall = open_kendall
            # atual_max_kendall = max_kendall
            # atual_min_kendall = min_kendall
            atual_close_kendall = close_kendall
            atual_tipo_kendall = type_kendall(atual_open_kendall, atual_close_kendall)

            if atual_tipo_kendall == 1:
                atual_suporte_kendall = atual_open_kendall
                atual_resistencia_kendall = atual_close_kendall
            else:
                atual_suporte_kendall = atual_open_kendall
                atual_resistencia_kendall = atual_close_kendall

        if atual_resistencia_kendall < resistencia_kendall and (resistencia < max_kendall or resistencia == 0):
            resistencia = max_kendall

        if atual_suporte_kendall > suporte_kendall and (suporte > min_kendall or suporte == 0):
            suporte = min_kendall

        if i <= t and suporte > 0 and resistencia > 0 and suporte < suporte_kendall:
            qtd_suporte, qtd_resistencia, x = seis_anteriores(candles, i, ttl)
            if qtd_suporte == 6 or qtd_resistencia == 6:
                break

        i = i - 1

    total = resistencia - suporte
    divisao = total / 2
    tendencia = 1 if atual_close_kendall > (suporte + divisao) else -1

    return suporte, resistencia, tendencia, atual_close_kendall, atual_tipo_kendall


def fibonacci(suporte, resistencia, tendencia):
    total = resistencia - suporte
    zero_cinquenta = (total / 100) * 50
    zero_meia_um = (total / 100) * 61
    zero_sete_oito_meia = (total / 100) * Decimal(78.6)

    if tendencia == 1:
        return (resistencia - zero_cinquenta), (resistencia - zero_meia_um), (resistencia - zero_sete_oito_meia)
    else:
        return (suporte + zero_cinquenta), (suporte + zero_meia_um), (suporte + zero_sete_oito_meia)


def dentro_fibonacci(cripto, tendencia, close_kendall, atual_tipo_kendall, zero_cinquenta, zero_meia_um,
                     zero_sete_oito_meia):
    if tendencia == 1 and atual_tipo_kendall == 1:
        if close_kendall <= zero_cinquenta and close_kendall >= zero_meia_um:
            return True, "*Cripto:* " + cripto + "\n*Tendencia de alta* \nFibonacci marcando entre *0.5 e 0.618*\nAção: *Vender*"
        elif close_kendall <= zero_meia_um and close_kendall >= zero_sete_oito_meia:
            return True, "*Cripto:* " + cripto + "\n*Tendencia de alta* \nFibonacci marcando entre *0.618 e 0.786*\nAção: *Vender*"
    else:
        if close_kendall >= zero_cinquenta and close_kendall <= zero_meia_um:
            return True, "*Cripto:* " + cripto + "\n*Tendencia de baixa* \nFibonacci marcando entre *0.5 e 0.618*\nAção: *Comprar*"
        elif close_kendall >= zero_meia_um and close_kendall <= zero_sete_oito_meia:
            return True, "*Cripto:* " + cripto + "\n*Tendencia de baixa* \nFibonacci marcando entre *0.618 e 0.786*\nAção: *Comprar"
    return False, ""


def send(msg, token=api_key_telagram):
    chat_id = -1001360328913  # -527092110
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)


# 0, 1
# x=[32699.9, 32798.5]

# t = rf_signals.rng_size(x, 3.5, 20)
# n = 20
# qty = 3.5
# wper      = (n*2) - 1

# print('teste')
# time.sleep(11111111)

def sma(can, i, y):
    # y = 15
    i = len(can) - i if (i + y) > len(can) else i

    sum = float(0.0)
    for ii in range(0, y):
        # if i < 400:
        sum = float(sum) + float(can[(i + ii)][4]) / float(y)

    return sum


def ema(can, x, length=15):
    # pprint(can)
    i = len(can) - x if (x + length) > len(can) else len(can) - 1
    t = len(can) - x if (x + length) > len(can) else length - 1
    # can = []
    # print(can[1][0]) recente
    # print(can[2][0]) antigo
    sum = []
    y = 0
    while y < len(can):
        # can.append(candles[i])
        sum.append(float(0.0))
        y = y + 1

    i = len(can) - x if (x + length) > len(can) else len(can) - length - 1

    sum_ant = 0.0
    while i >= 0:
        # length = 15
        alpha = 2 / (length + 1)

        # if i < 400:
        # sum[i] = float(alpha * float(can[i][4]) + (1 - alpha) * nz(sum[i + 1]))
        if not isnumber(sum_ant) or sum_ant == 0.0:
            try:
                sum_ant = sma(can, i + 1, length)
            except:
                sum_ant = 0.0
                pass
        try:
            try:
                try:
                    sum[i] = float(alpha) * float(can[i][4]) + float(1 - alpha) * sum_ant  # float(nz(sum[i+1]))
                except:
                    sum[i] = sum_ant
                    pass
            except:
                print(i)
                sum[i] = 0.0
                pass
        except:
            print(i)
            sum[i] = 0.0
            pass
        # sum[i] = float(alpha) * float(can[i][4])# + float(1 - alpha) * float(nz(sum[i]))
        sum_ant = sum[i]
        i = i - 1

    return sum[x]


# Range Size Function
def rng_size(x, qty, n, i):
    wper = (n * 2) - 1
    # print(x[i][0])
    # print(abs(x[i][0] - x[1][0]))
    # ema(can, i, 15)
    # print('reeee1')
    avrng = ema(abs(x[i][0] - x[1][0]), i, n)
    # print('reeee2')
    AC = ema(avrng, i, wper) * qty
    return AC


'''
i = len(can) - 1
# can = []
sum = []

while i >= 0:
    # can.append(candles[i])
    sum.append(float(0.0))
    i = i - 1

i = len(can) - 1
while i >= 0:
    # length = 15
    alpha = 2 / (length + 1)

    if i < 400:
        sum[i] = float(alpha * float(can[i][4]) + (1 - alpha) * nz(sum[i + 1]))
    i = i - 1

return sum[x]'''


def isnumber(value):
    try:
        float(value)
    except ValueError:
        return False
    return True


def nz(x):
    return (x if isnumber(x) else 0)


def operacaoCriptoNova(client, exchange_info, compra_cripto):
    for s in exchange_info['symbols']:
        if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT':
            candles = client.get_klines(symbol=s['symbol'], interval=Client.KLINE_INTERVAL_1MINUTE)
            # print(s['baseAsset'] + "/" + s['quoteAsset'] + " - Kendle: " + str(len(candles)))
            if len(candles) <= 3:
                check_buy = False
                try:
                    compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY")
                    check_buy = True
                except:
                    check_buy = False
                    pass

                if not check_buy:
                    # client.order_market_buy(symbol='BNBBTC',quantity=100)
                    ticker = client.get_symbol_ticker(symbol=str(s['baseAsset'] + s['quoteAsset']))
                    price = float(ticker['price'])
                    client.order_market_buy(symbol=str(s['baseAsset'] + s['quoteAsset']),
                                            quantity=(math.ceil(10 / price) + 1 if price < 1 else 11))
                    compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY")
                    msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - Kendle: " + str(len(candles)) + " - BUY (" + str(
                        float(balance['free']) * price) + ")"
                    print(msg)
                    send(msg, token=api_key_telagram)

            elif len(candles) > 6 and len(candles) <= 60:

                check_buy = False
                try:
                    compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY")
                    check_buy = True
                except:
                    check_buy = False
                    pass

                check_sell = False
                try:
                    compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-SELL")
                    check_sell = True
                except ValueError:
                    check_sell = False
                    pass

                if (check_buy and len(candles) <= 10 and not check_sell) or not check_sell:
                    # client.order_market_sell(symbol='BNBBTC',quantity=100)
                    ticker = client.get_symbol_ticker(symbol=str(s['baseAsset'] + s['quoteAsset']))
                    price = float(ticker['price'])
                    balance = client.get_asset_balance(asset=s['baseAsset'])
                    client.order_market_sell(symbol=str(s['baseAsset'] + s['quoteAsset']),
                                             quantity=float(balance['free']))
                    compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-SELL")
                    msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - Kendle: " + str(
                        len(candles)) + " - SELL (" + str(float(balance['free']) * price) + ")"
                    print(msg)
                    send(msg, token=api_key_telagram)


'''
#Inicio novo
exchange_info = client.get_exchange_info()

for s in exchange_info['symbols']:
    if s['status'] == 'TRADING' and (s['baseAsset'] == 'BTC' and (s['quoteAsset'] == 'USDT')):
        candles = client.get_klines(symbol=s['symbol'], interval=Client.KLINE_INTERVAL_1HOUR)
        i = len(candles) - 1

        #Transforma do recente para o mais antigo
        can = []
        while i >= 0:
            can.append(candles[i])
            i = i - 1

        # Transforma do recente para o mais antigo
        i = len(candles) - 1
        resistencia1 = 0
        resistencia = [1][0]
        resistencia = [2][0]
        suporte = 0
        while i >= 1:
            if resistencia1 == 0 or resistencia1 < candles[i][4] if candles[i][1] < candles[i][4] else candles[i][1]:
                resistencia = candles[i][4] if candles[i][1] < candles[i][4] else candles[i][1]
            i = i - 1

        print(candles[498][0])
        print(candles[498][4])
        print(candles[499][0])
        print(candles[499][4])
        print('------')
        #Maior, mais recente 498 = 20:00 e 499 = 21:00

time.sleep(10000)
#Fim novo
'''


def inverteSeguenciaIndex(candles):
    i = len(candles) - 1
    can = []
    while i >= 0:
        can.append(candles[i])
        i = i - 1

    return can


'''inicio ema '''


def cruzamentoEMA(candles, compra_cripto):
    can = inverteSeguenciaIndex(candles)

    '''print(str(int(can[1][0])) + " " +str(int(can[200][0])) + " -- Close- " + str(can[i][4]) + " -- SMA- " + str(
        sma(can, 2, 15)) + " -- EMA 200- " + str(ema(can, 1, 200)) +" -- EMA 50- " + str(ema(can, 1, 50)))'''

    check_buy = False
    try:
        compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY")
        check_buy = True
    except:
        check_buy = False
        pass

    check_buy2 = False

    try:
        compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY2")
        check_buy2 = True
    except:
        check_buy2 = False
        pass

    # print(str(not check_buy and ema(can, 3, 50) < ema(can, 3, 200) and ema(can, 0, 50) >= ema(can, 0, 200))+' ---- ' + str(not check_buy2 and ema(can, 3, 50) > ema(can, 3, 200) and ema(can, 0, 50) <= ema(can, 0, 200)))

    if not check_buy and ema(can, 3, 50) < ema(can, 3, 200) and ema(can, 0, 50) >= ema(can, 0, 200):
        compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY")
        '''print(str(int(can[1][0])) + " " + str(int(can[200][0])) + " -- Close- " + str(
        can[i][4]) + " -- SMA- " + str(
        sma(can, 2, 15)) + " -- EMA 200- " + str(ema(can, 1, 200)) + " -- EMA 50- " + str(ema(can, 1, 50)))'''

        msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - Timestamp: " + str(can[0][0]) + " - Valor: " + str(
            can[0][4]) + " - BUY"
        print(msg)
        send(msg, token=api_key_telagram)

    if not check_buy2 and ema(can, 1, 50) > ema(can, 1, 200) and ema(can, 0, 50) <= ema(can, 0, 200):
        compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY2")
        '''print(str(int(can[1][0])) + " " + str(int(can[200][0])) + " -- Close- " + str(
        can[i][4]) + " -- SMA- " + str(
        sma(can, 2, 15)) + " -- EMA 200- " + str(ema(can, 1, 200)) + " -- EMA 50- " + str(ema(can, 1, 50)))'''

        msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - Timestamp: " + str(can[0][0]) + " - Valor: " + str(
            can[0][4]) + " - SELL"
        print(msg)
        send(msg, token=api_key_telagram)


def macd(can, i):
    fast_length = 12
    slow_length = 26
    signal_length = 9

    '''
    i = len(candles) - 1
    can = []
    while i >= 0:
        can.append(candles[i])
        i = i - 1'''

    # ema(can, 3, 50) < ema(can, 3, 200) and ema(can, 0, 50) >= ema(can, 0, 200):

    macd = []
    x = 0
    while x < len(can):
        # can.append(candles[i])
        macd.append([can[x][0], can[x][1], can[x][2], can[x][3], '0.0', '0.0', '0.0'])
        x = x + 1

    x = 0
    while x < len(can):
        fast_ma = ema(can, x, fast_length)
        slow_ma = ema(can, x, slow_length)
        macd[x][4] = fast_ma - slow_ma
        x = x + 1

    x = 0
    while x < len(can):
        macd[x][5] = ema(macd, x, signal_length)
        x = x + 1

    # macd[x][5] = signal
    # macd[i][6] = hist

    try:
        signal = ema(macd, i, signal_length)
        macd[i][6] = macd[i][4] - macd[i][5]
        macd[i + 1][6] = macd[i + 1][4] - macd[i + 1][5]

        t = (2 if macd[i + 1][6] < macd[i][6] else 1) if macd[i][6] >= 0 else (
            -1 if macd[i + 1][6] < macd[i][6] else -2)
        fast_ma = ema(can, i, fast_length)
        slow_ma = ema(can, i, slow_length)
        # hist = macd - signal
        returno = fast_ma, slow_ma, signal, macd[i][6], t
    except OSError as e:
        returno = 0, 0, 0, 0, 0
        pass
    return returno


def sendMacd(v0, v1, compra_cripto):
    v0 = macd(can, 0)[4]
    v1 = macd(can, 1)[4]

    check_buy = False
    try:
        compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY")
        check_buy = True
    except:
        check_buy = False
        pass

    check_buy2 = False

    try:
        compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY2")
        check_buy2 = True
    except:
        check_buy2 = False
        pass

    if not check_buy and (v0 == 1 or v0 == 2) and (v1 == -1 or v1 == -2):
        compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY")
        msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - MACD: " + str(
            can[0][0]) + " - Valor: " + str(can[0][4]) + " - BUY"
        print(msg)
        send(msg, token=api_key_telagram)

    if not check_buy2 and (v0 == -1 or v0 == -2) and (v1 == 1 or v1 == 2):
        compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY2")
        msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - MACD: " + str(
            can[0][0]) + " - Valor: " + str(can[0][4]) + " - SELL"
        print(msg)
        send(msg, token=api_key_telagram)


def sendMacd2(v0, v1, compra_cripto, compra_cripto_valor):
    v0 = macd(can, 0)[4]
    v1 = macd(can, 1)[4]

    check_buy = False
    try:
        compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY")
        check_buy = True
    except:
        check_buy = False
        pass

    check_buy2 = False

    try:
        compra_cripto.index(s['baseAsset'] + s['quoteAsset'] + "-BUY2")
        check_buy2 = True
    except:
        check_buy2 = False
        pass

    if not check_buy and (v0 == 1 or v0 == 2) and (v1 == -1 or v1 == -2):
        compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY")
        compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY")
        msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - MACD: " + str(
            can[0][0]) + " - Valor: " + str(can[0][4]) + " - BUY"
        print(msg)
        send(msg, token=api_key_telagram)

    if check_buy and not check_buy2 and (v0 == -1 or v0 == -2) and (v1 == 1 or v1 == 2):
        compra_cripto.append(s['baseAsset'] + s['quoteAsset'] + "-BUY2")
        msg = s['baseAsset'] + "/" + s['quoteAsset'] + " - MACD: " + str(
            can[0][0]) + " - Valor: " + str(can[0][4]) + " - SELL"
        print(msg)
        send(msg, token=api_key_telagram)


def mediaVolume(can, i, y):
    volume = 0.0

    t = (i + y) - 1

    x = len(can) - 1 if t > (len(can) - 1) else t
    while x > i:
        volume = volume + float(can[x][5])
        x = x - 1

    return float(volume / y)


def fibo(can, i):
    resistencia = float(can[i][4])
    suporte = float(can[i][4])

    zona_zero = 0
    r = 0
    s = 0
    x = i
    while x < len(can):
        direcao = 1 if float(can[x][4]) >= float(can[x][1]) else -1

        if float(can[x][2]) > resistencia and float(can[x][2]) >= float(can[i][2]):
            resistencia = float(can[x][2])
            r = x

        if float(can[x][3]) < suporte and float(can[x][3]) <= float(can[i][3]):
            suporte = float(can[x][3])
            s = x

        # if float(can[x][2]) > float(can[0][4]) and float(can[x][3]) < float(can[0][4]):
        #    zona_zero = zona_zero + 1

        # zona_zero == 3 or

        if ((direcao == 1 and float(can[x][4]) < (
        float(can[x - 3][4]) if float(can[x - 3][4]) > float(can[x - 3][1]) else float(can[x - 3][1])) and float(
                can[x][4]) > (
             float(can[x - 4][1]) if float(can[x - 4][1]) < float(can[x - 4][4]) else float(can[x - 4][4])))) and (
                float(can[x][2]) > float(can[i][3])) and float(resistencia) > float(
                can[i][2]):  # and suporte < can[x][4]:
            break

        '''if x >= 50:
            print(str(resistencia))
            time.sleep(10000)'''

        x = x + 1

    # resistencia = 49841.41
    # suporte = 48316.84
    # can[i][4] = 48980

    total = resistencia - suporte
    atual = float(can[i][4]) - suporte
    fi = (atual / total)

    '''
    anterior = 0
    proximo = 0

    # n = 664.16
    n = total

    while (proximo < n):
        print(proximo)
        proximo = proximo + anterior
        anterior = proximo - anterior
        if (proximo == 0):
            proximo = proximo + 1
    '''

    # 1 = tendencia de alta; -1 = tendencia de baixa
    return suporte, resistencia, 1 if r < s else -1, float('{:.3f}'.format(fi))


def projecaoFibo(suporte, resistencia, direcao, marcacao_fibo=38.2):
    diferenca = resistencia - suporte
    sobra = diferenca * (100 - marcacao_fibo)
    if direcao == 1:
        nova_resistencia = sobra + diferenca + suporte
    else:
        novo_suporte = sobra + diferenca + resistencia

    return direcao, nova_resistencia if direcao == 1 else novo_suporte


def localizaPosicaoVetor(vet, seach):
    i = 0
    for v in vet:
        if v[0] == seach:
            return i
        i = i + 1


def sendFibo(compra_cripto, can, i):
    suporte, resistencia, direcao_fibo, fiboAtual = fibo(can, i)
    mma20 = ema(can, i, 20)
    mediaVol = mediaVolume(can, i, 50)
    direcao, novo_valor = projecaoFibo(suporte, resistencia, direcao_fibo, 38.2)

    loc_buy = localizaPosicaoVetor(compra_cripto, s['baseAsset'] + s['quoteAsset'] + "-BUY")
    # loc_sell = localizaPosicaoVetor(compra_cripto, s['baseAsset'] + s['quoteAsset'] + "-BUY2")

    if loc_buy == None:
        check_buy = False
    else:
        check_buy = True

    '''
    if loc_sell == None:
        check_sell = False
    else:
        check_sell = True'''

    if not check_buy and mediaVol < float(can[0][5]) and fiboAtual >= 0.618 and fiboAtual < 0.786 and direcao == 1:
        compra_cripto.append([s['baseAsset'] + s['quoteAsset'] + "-BUY", novo_valor, float(can[0][4])])
        m = (1 if mma20 >= float(can[0][3]) else 0)

        msg = s['baseAsset'] + "/" + s['quoteAsset'] + 'FIBO 0.618 (' + str(fiboAtual) + ')' + " - " + str(
            'MMA20' if m == 1 else '') + " - Valor: " + str(can[0][4]) + " - BUY"
        print(msg)
        send(msg, token=api_key_telagram)

    elif check_buy and direcao == 1 and float(can[0][4]) >= compra_cripto[loc_buy][1]:
        msg = s['baseAsset'] + "/" + s['quoteAsset'] + 'FIBO 0.618 (' + str(fiboAtual) + ')' + " -- Compra: " + str(
            compra_cripto[loc_buy][2]) + " - Valor: " + str(can[0][4]) + " - SELL"
        print(msg)
        send(msg, token=api_key_telagram)
        compra_cripto.pop(loc_buy)


def localizaCritpoPorValorPeriodo(can, vlt_a):
    # vlt_a = 2.3521334

    if (float(can[2][2]) >= vlt_a and float(can[2][3]) <= vlt_a) or (
            float(can[3][2]) >= vlt_a and float(can[3][3]) <= vlt_a):
        pprint(s['baseAsset'])
        # 12:28
        # 2881


def previsao_tendencia_ajuste(top200, top_linha_200, top50, top_linha_50):
    dif = top200 - top50 if top200 > top50 else top50 - top200
    qtd = top_linha_200 - top_linha_50
    if qtd > 0:
        vlr_diario = dif / qtd

        if top200 > top50:
            previsao = top200 - (vlr_diario * top_linha_200)
        else:
            previsao = top200 + (vlr_diario * top_linha_200)
    else:
        previsao = 0

    return previsao

def linhaTendenciaResistencia(can, qtd_velas):
    i = 0

    top50, top_linha_50, top100, top_linha_100, top150, top_linha_150, top200, top_linha_200 = 0, 0, 0, 0, 0, 0, 0, 0

    while i <= qtd_velas:
        close = float(can[i][4])
        open = float(can[i][1])

        valor_maior = close if close > open else open
        valor_menor = close if close < open else open

        quartil = 50 if i <= 50 else 100 if i > 50 and i <= 100 else 150 if i > 100 and i <= 150 else 200 if i > 150 else 200

        if quartil == 50:
            if top50 < valor_maior:
                top50 = valor_maior
                top_linha_50 = i
        elif quartil == 100:
            if top100 < valor_maior:
                top100 = valor_maior
                top_linha_100 = i
        elif quartil == 150:
            if top150 < valor_maior:
                top150 = valor_maior
                top_linha_150 = i
        elif quartil == 200:
            if top200 < valor_maior:
                top200 = valor_maior
                top_linha_200 = i


        i = i + 1

    t50 = previsao_tendencia_ajuste(top200, top_linha_200, top50, top_linha_50)
    t100 = previsao_tendencia_ajuste(top200, top_linha_200, top100, top_linha_100)
    t150 = previsao_tendencia_ajuste(top200, top_linha_200, top150, top_linha_150)

    if t50 > t100 and t50 > t150:
        previsao = t50
    elif t100 > t50 and t100 > t150:
        previsao = t100
    elif t150 > t50 and t150 > t100:
        previsao = t150
    else:
        previsao = top200


    return top200, top50, previsao


def linhaTendenciaSuporte(can, qtd_velas):
    i = 0

    top50, top_linha_50, top100, top_linha_100, top150, top_linha_150, top200, top_linha_200 = 0, 0, 0, 0, 0, 0, 0, 0

    while i <= qtd_velas:
        close = float(can[i][4])
        open = float(can[i][1])

        valor_maior = close if close > open else open
        valor_menor = close if close < open else open

        quartil = 50 if i <= 50 else 100 if i > 50 and i <= 100 else 150 if i > 100 and i <= 150 else 200 if i > 150 else 200

        if quartil == 50:
            if top50 > valor_menor or top50 == 0:
                top50 = valor_menor
                top_linha_50 = i
        elif quartil == 100:
            if top100 > valor_menor or top100 == 0:
                top100 = valor_menor
                top_linha_100 = i
        elif quartil == 150:
            if top150 > valor_menor or top150 == 0:
                top150 = valor_menor
                top_linha_150 = i
        elif quartil == 200:
            if top200 > valor_menor or top200 == 0:
                top200 = valor_menor
                top_linha_200 = i


        i = i + 1

    if top150 < top200 and top150 < top100 and top150 < top50:
        top200 = top200
        top_linha_200 = top_linha_150
    elif top100 < top200 and top100 < top150 and top100 < top50:
        top200 = top100
        top_linha_200 = top_linha_100
    elif top50 < top200 and top50 < top100 and top50 < top150:
        top200 = top50
        top_linha_200 = top_linha_50



    t50 = previsao_tendencia_ajuste(top200, top_linha_200, top50, top_linha_50)
    t100 = previsao_tendencia_ajuste(top200, top_linha_200, top100, top_linha_100)
    t150 = previsao_tendencia_ajuste(top200, top_linha_200, top150, top_linha_150)

    if t50 > t100 and t50 > t150 and t50 > 0:
        previsao = t50
    elif t100 > t50 and t100 > t150 and t100 > 0:
        previsao = t100
    elif t150 > t50 and t150 > t100 and t150 > 0:
        previsao = t150
    else:
        previsao = top200


    return top200, top50, previsao


compra_cripto = []
while 1:
    try:
        while 1:
            if client is None:
                client = Client(api_key, api_secret)

            exchange_info = client.get_exchange_info()

            for s in exchange_info['symbols']:
                if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT' and s['baseAsset'] == 'ADA':  # and s['baseAsset'] == 'XRP':
                    candles = client.get_klines(symbol=s['symbol'], interval=Client.KLINE_INTERVAL_1DAY)

                    can = inverteSeguenciaIndex(candles)
                    # pprint(str(fibo(can, 0)) + ' ----fibo ' + str(fibo(can, 7)) + ' ----ema: ' + str(ema(can, 0, 20)))

                    # sendFibo(compra_cripto, can, 0)

                    # localizaCritpoPorValorPeriodo(can, 2.3521334)
                    print(s['baseAsset'])
                    print(linhaTendenciaResistencia(can, 200))
                    print(linhaTendenciaSuporte(can, 200))
                    dd = 0  # 200
                    '''while dd <= 200:  # dd >=0:
                        print(str(float(can[dd][1])) + str(';') + str(float(can[dd][2])) + str(';') + str(
                            float(can[dd][3])) + str(';') + str(float(can[dd][4])) + str(';') + str(
                            float(can[dd][5])) + str(';') + str(can[dd][6]))
                        # dd = dd - 1
                        dd = dd + 1'''
                    # pprint(estouroCima(can))
                    time.sleep(10000)

                    '''can = inverteSeguenciaIndex(candles)
                    v0 = macd(can, 0)[4]
                    v1 = macd(can, 1)[4]

                    sendMacd(v0, v1, compra_cripto)'''

                    # cruzamentoEMA(candles, compra_cripto)

            print(datetime.now())

    except OSError as e:
        print('error: ' + str(e) + ' -- ' + str(datetime.now()))
        time.sleep(60)
        pass

time.sleep(10000)
'''fim ema'''
compra_cripto = []
while 1:
    try:
        while 1:
            if client is None:
                client = Client(api_key, api_secret)

            exchange_info = client.get_exchange_info()

            # operacaoCriptoNova(client, exchange_info, compra_cripto)
            print(datetime.now())
    except e:
        time.sleep(10)
        pass

    # for s in exchange_info['symbols']:
    #    if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT' and  len(client.get_klines(symbol=s['symbol'], interval=Client.KLINE_INTERVAL_30MINUTE)) <500:
    #        compra_cripto.append(s['baseAsset'])
    # pprint(compra_cripto)

time.sleep(10000)
# while True:
for s in exchange_info['symbols']:
    # and s['baseAsset'] == 'CHZ'
    # if s['status'] == 'TRADING' and ((s['baseAsset'] == 'BTC' or s['baseAsset'] == 'BNB' or s['baseAsset'] == 'ETH' or s['baseAsset'] == 'ETC' or s['baseAsset'] == 'DOGE' or s['baseAsset'] == 'WAVES' or s['baseAsset'] == 'ADA' or s['baseAsset'] == 'LTC' or s['baseAsset'] == 'CHZ' or s['baseAsset'] == 'XRP' or s['baseAsset'] == 'BTT') and (s['quoteAsset'] == 'USDT')): # and s['symbol']=='DOGEUSDT':

    # print(s['status'] + " -- " + str(s['baseAsset']) + " - - " + s['quoteAsset'])
    if s['status'] == 'TRADING' and (s['baseAsset'] == 'BTC' and (s['quoteAsset'] == 'USDT')):
        candles = client.get_klines(symbol=s['symbol'], interval=Client.KLINE_INTERVAL_15MINUTE)

        i = len(candles) - 1

        can = []
        while i >= 0:
            can.append(candles[i])
            i = i - 1

        i = len(can) - 1

        # 1499040000000,  # Open time
        # "0.01634790",  # Open
        # "0.80000000",  # High
        # "0.01575800",  # Low
        # "0.01577100",  # Close
        # "148976.11427815",  # Volume
        # 1499644799999,  # Close time
        # "2434.19055334",  # Quote asset volume
        # 308,  # Number of trades
        # "1756.87402397",  # Taker buy base asset volume
        # "28.46694368",  # Taker buy quote asset volume
        # "17928899.62484339"  # Can be ignored

        while i >= 0:
            # ts = int(can[i][0])

            qty = 3.5
            n = 20
            # pprint(rng_size(can, qty, n, i))

            print(str(int(can[i][0])) + " -- Close- " + str(can[i][4]) + " -- EMA- " + str(
                ema(can, i, 15)) + " -- SMA- " + str(sma(can, i, 15)))
            i = i - 1

        '''
        i = len(candles) - 1
        can = []
        sum = []

        while i >= 0:
            can.append(candles[i])
            sum.append(float(0.0))
            i=i-1

        i = len(can)-1
        while i>=0:

            #y = 15
            #sum = float(0.0)
            #for ii in range(0, y):
            #    if i < 400:
            #        sum = float(sum) + float(can[(i+ii)][4]) / float(y)
            #        #pprint(" -- " + str(can[ii][4]) + " -- " + str(can[ii][0]) + " -- " + str(sum))

            #sum = sma(can, i, 15)

            length = 15

            alpha = 2 / (length + 1)

            if i < 400:
                #sum = sum + (
                #sum = sma(can, i, length) #if math.isnan(sum[1]) else alpha * can[i] + (1 - alpha) * (sum[1] if math.isnan(sum[1]) else 0))
                print(i)
                print(alpha * float(can[i][4]) + (1 - alpha) * nz(sum[i+1]))# + (1 - alpha) * nz(sum[i+1])
                print('')
                #pprint(float(sma(can, i, length) if isnumber(sum[i+1]) else alpha * float(can[i][4]) + (1 - alpha) * nz(sum[i+1])))
                print(float(alpha * float(can[i][4]) + (1 - alpha) * nz(sum[i+1])))
                sum[i] = float(alpha * float(can[i][4]) + (1 - alpha) * nz(sum[i+1]))

                pprint("time: "+str(can[i][0]) + " -- " +str(can[i][4]) + " -- " + str(can[i][0]) + " -- " + str(sum[i]))

    
        i=i-1

    #pprint(candles[i])
    '''

        print(123)
        time.sleep(111110)

    # suporte, resistencia, tendencia, atual_close_kendall,atual_tipo_kendall = suporte_resistencia(candles)

    # zero_cinquenta, zero_meia_um, zero_sete_oito_meia = fibonacci(suporte, resistencia, tendencia)

    '''print()
        print('symbol: '+str(s['symbol']))
        print('suporte: '+str(suporte))
        print('resistencia: '+str(resistencia))
        print('tendencia: '+str(tendencia))
        print('zero_cinquenta: '+str(zero_cinquenta))
        print('zero_meia_um: '+str(zero_meia_um))
        print('zero_sete_oito_meia: '+str(zero_sete_oito_meia))
        print('atual_close_kendall: '+str(atual_close_kendall))'''

    # i=1
    # for k in candles:
    # pprint(k)

    # print('New')
    # print(i)
    # i=i+1
    #
    # # //-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # # //Inputs
    # # //-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    # # //Range Source
    # rng_src = k[4]#'close'  # input(defval=close, type=input.source, title="Swing Source")
    #
    # # //Range Period
    # rng_per = 20  # input(defval=20, minval=1, title="Swing Period")
    #
    # # //Range Size Inputs
    # rng_qty = 3.5  # input(defval=3.5, minval=0.0000001, title="Swing Multiplier")
    #
    # # //Bar Colors
    # use_barcolor = False  # input(defval=false, type=input.bool, title="Bar Colors On/Off")
    #
    # # //-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # # //Definitions
    # # //-----------------------------------------------------------------------------------------------------------------------------------------------------------------
    #
    # # //Range Filter Values
    # [h_band, l_band, filt] = rf_signals.rng_filt(rng_src, rf_signals.rng_size(rng_src, rng_qty, rng_per), rng_per)
    #
    # # //Direction Conditions
    # fdir = 0.0
    # fdir = 1 if filt > filt[1] else -1 if filt < filt[1] else fdir
    # upward = 1 if fdir == 1 else 0
    # downward = 1 if fdir == -1 else 0

    # print(str(k[0])+" - upward: "+str(upward)+" - downward: "+str(downward))
    #
    # # //Trading Condition
    # longCond = rng_src > filt and rng_src > rng_src[1] and upward > 0 or rng_src > filt and rng_src < rng_src[1] and upward > 0
    # shortCond = rng_src < filt and rng_src < rng_src[1] and downward > 0 or rng_src < filt and rng_src > rng_src[1] and downward > 0
    #
    # CondIni = 0
    # CondIni = 1 if longCond else -1 if shortCond else CondIni[1]
    # CondIni = longCond ? 1 : shortCond ? -1 : CondIni[1]
    # longCondition = longCond and CondIni[1] == -1
    # shortCondition = shortCond and CondIni[1] == 1
    #
    # # //Colors
    # filt_color = '#05ff9b' if upward else '#ff0583' if downward else '#cccccc'
    # bar_color = ('#05ff9b' if rng_src > rng_src[1] else '#00b36b') if upward and (rng_src > filt) else (
    #     '#ff0583' if rng_src < rng_src[1] else '#b8005d') if downward and (rng_src < filt) else '#cccccc'

    # enviar_mensagem, msg = dentro_fibonacci(s['symbol'], tendencia, atual_close_kendall, atual_tipo_kendall, zero_cinquenta, zero_meia_um, zero_sete_oito_meia)

    # if enviar_mensagem:
    #    print(msg)
    #    print()
    #    #send(msg, token=api_key_telagram)

time.sleep(60)

# pprint(client.get_all_orders(symbol='DOGEUSDT'))

# teste = busca(exchange_info['symbols'], 'DOGEUSDT')
# pprint(teste)
# pprint(exchange_info['symbols'][0])
# for s in exchange_info['symbols']:
#    print(s)
