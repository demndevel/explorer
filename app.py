from web3 import Web3
from flask import Flask, render_template, send_file, request, redirect
import json

config = open('config.json')
cfg = json.load(config)

coinName = cfg['coinName']
coinSymbol = cfg['coinSymbol']
coinSymbolLower = cfg['coinSymbolLower']
rpcUrl = cfg['rpcUrl']

app = Flask(__name__)
web3 = Web3(Web3.HTTPProvider(rpcUrl))


@app.route("/static/<file>")
def style(file):
    return send_file("static/{file}".format(file=file))


@app.route("/")
def index():
    account = request.cookies.get('account')
    print(account)
    if account is None:
        account = "<a class=\"enableEthereumButton upperRight\">Connect MetaMask</a>"
    else:
        acc = account
        acc = web3.toChecksumAddress(acc)
        account = "<p class=\"upperRight\" style=\"margin-right: 44ch;\">Your address: </p><a class=\"upperRight\" href=\"/account/{acc}\">{acc}</a>".format(acc=acc)
    latestBlock = web3.eth.block_number
    gasPrice = web3.fromWei(web3.eth.gasPrice, "gwei")
    return render_template("index.html", coinSymbolLower=coinSymbolLower, latestBlock=latestBlock, gasPrice=gasPrice, account=account)

# --- API block --- #


@app.route("/api/block/<int:number>")
def api_block(number):
    block = web3.eth.get_block(number)
    return str(block)[14:-1]


@app.route("/api/txhash/<txhash>")
def api_txhash(txhash):
    tx = str(web3.eth.getTransaction(txhash))
    return tx


@app.route("/api/balance/<address>")
def api_balance(address):
    balance = str(web3.eth.getBalance(address))
    return balance
# --- End API block --- #

# --- Explorer block --- #


@app.route("/block/<int:number>")
def block(number):

    try:
        block = web3.eth.get_block(number)
    except:
        return render_template("error.html", error="Block not found", coinSymbolLower=coinSymbolLower)
    difficulty = block['difficulty']
    extraData = block["extraData"].hex()
    gasLimit = block["gasLimit"]
    gasUsed = block["gasUsed"]
    hash = block["hash"].hex()
    if int(block["logsBloom"].hex(), 16) == 0:
        logsBloom = "0x0"
    else:
        logsBloom = block["logsBloom"].hex()

    miner = block["miner"]
    mixHash = block["mixHash"].hex()
    nonce = block["nonce"].hex()
    number = block["number"]
    parentHash = block["parentHash"].hex()
    receiptsRoot = block["receiptsRoot"].hex()
    sha3Uncles = block["sha3Uncles"].hex()
    size = block["size"]
    stateRoot = block["stateRoot"].hex()
    timestamp = block["timestamp"]
    totalDifficulty = block["totalDifficulty"]

    if not block['transactions']:
        transactions = "None"
    else:
        transactions = block['transactions']

    transactionsRoot = block["transactionsRoot"].hex()
    global uncles
    uncles = block["uncles"]

    return render_template("block.html", difficulty=str(difficulty), extraData=str(extraData),
                           gasLimit=str(gasLimit), gasUsed=str(gasUsed),
                           hash=str(hash), logsBloom=str(logsBloom),
                           miner=str(miner), mixHash=str(mixHash),
                           nonce=str(nonce), number=str(number),
                           parentHash=str(parentHash), receiptsRoot=str(receiptsRoot),
                           sha3Uncles=str(sha3Uncles), size=str(size),
                           stateRoot=str(stateRoot), timestamp=str(timestamp),
                           totalDifficulty=str(totalDifficulty), transactions=str(transactions),
                           transactionsRoot=str(transactionsRoot), uncles=str(uncles), coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)


@app.route("/block/<int:number>/uncles")
def uncles(number):
    try:
        block = web3.eth.get_block(number)
    except:
        return render_template("error.html", error="Block not found")
    uncles = block["uncles"]
    number = block["number"]
    parsed = []
    for uncle in uncles:
        parsed.append(str(uncle.hex()))
    return render_template("uncles.html", uncles=parsed, number=number, coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)


@app.route("/block/<int:number>/transactions")
def transactions(number):
    try:
        block = web3.eth.get_block(number)
    except:
        return render_template("error.html", error="Block not found", coinSymbolLower=coinSymbolLower)

    transactions = block["transactions"]
    number = block["number"]
    parsed = []
    for transaction in transactions:
        parsed.append(str(transaction.hex()))
    if not parsed:
        parsed = ["None"]
    return render_template("transactions.html", transactions=parsed, number=number, coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)


@app.route("/bloominfo/<int:block>")
def bloominfo(block):
    try:
        block = web3.eth.get_block(block)
    except:
        return render_template("error.html", error="Block not found")
    bloom = block["logsBloom"].hex()
    blockNumber = block["number"]
    return render_template("bloominfo.html", bloom=bloom, blockNumber=blockNumber, coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)


@app.route("/account/<address>")
def account(address):
    balance = web3.eth.getBalance(address)
    nonce = web3.eth.getTransactionCount(address)
    balance_eth = web3.fromWei(balance, "ether")

    return render_template("account.html", address=address, balance_eth=balance_eth, nonce=str(nonce), coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)


@app.route("/tx/<txhash>")
def tx(txhash):
    try:
        tx = web3.eth.getTransaction(txhash)
    except:
        return render_template("error.html", error="Transaction not found")
    txFrom = tx["from"]
    txTo = tx["to"]
    txGas = tx["gas"]
    gasPriceWei = tx["gasPrice"]
    txGasPriceUnformatted = web3.fromWei(gasPriceWei, "ether")
    txGasPrice = format(txGasPriceUnformatted, '.18f')
    txHash = tx["hash"].hex()
    txNonce = tx["nonce"]
    txValueWei = tx["value"]
    txValueUnformatted = web3.fromWei(txValueWei, "ether")
    txValue = format(txValueUnformatted, '.18f')
    txBlockHash = tx["blockHash"]
    txBlockNumber = tx["blockNumber"]

    return render_template("tx.html", coinName=coinName, txFrom=txFrom, txTo=txTo, txGas=txGas, txGasPrice=txGasPrice,
                           txHash=txHash, txNonce=txNonce, txValue=txValue, txBlockHash=txBlockHash,
                           txBlockNumber=txBlockNumber, coinSymbol=coinSymbol, coinSymbolLower=coinSymbolLower)


@app.route('/', methods=['POST'])
def define_redirect():
    text = request.form['text']
    type = "a"
    if len(text) == 42 and text.startswith("0x"):
        type = "account"
    elif len(text) == 66 and text.startswith("0x"):
        type = "txhash"
    else:
        try:
            if int(text):
                type = "block"
        except:
            return render_template("error.html", error="Malformed input", coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)

    if type == "account":
        print(type)
        del type
        return redirect("/account/" + text)
    if type == "txhash":
        print(type)
        del type
        return redirect("/tx/" + text)
    if type == "block":
        print(type)
        del type
        return redirect("/block/" + text)

    return render_template("error.html", error="Malformed input", coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)


@app.route("/contractinfo")
@app.route("/contractInfo")
def contractinfo():
    return render_template("contractinfo.html", coinSymbolLower=coinSymbolLower, coinSymbol=coinSymbol)


# --- End Explorer block --- #
app.run(host="0.0.0.0")
