from src.binance_gold_tokens import BinanceGoldClient, BinanceGoldConfig, BinanceGoldError, build_metals_block


class FakeResponse:
    def __init__(self, payload): self.payload = payload
    def raise_for_status(self): return None
    def json(self): return self.payload


class FakeSession:
    def __init__(self): self.calls = []
    def get(self, url, params, timeout):
        self.calls.append((url, params, timeout))
        if url.endswith('/api/v3/exchangeInfo'):
            return FakeResponse({'symbols': [
                {'symbol': 'PAXGUSDT', 'status': 'TRADING'},
                {'symbol': 'XAUTUSDT', 'status': 'TRADING'},
            ]})
        rows = []
        base = 1000.0 if params['symbol'] == 'PAXGUSDT' else 2000.0
        for i in range(params['limit']):
            close = base + i
            rows.append([i * 3600000, str(close-1), str(close+1), str(close-2), str(close), '10', i*3600000+3599999, '10000', 5, '5', '5000', '0'])
        return FakeResponse(rows)


def test_public_binance_gold_analysis_has_no_auth_requirement():
    client = BinanceGoldClient(BinanceGoldConfig(max_bars=200), FakeSession())
    result = client.analyze('PAXG', '1H', 60)
    assert result['symbol'] == 'PAXGUSDT'
    assert result['source'] == 'BINANCE_SPOT'
    assert result['research_only'] is True
    assert result['live_execution'] is False
    assert result['indicators']['ema20'] is not None


def test_xaut_symbol_resolution_and_invalid_asset():
    client = BinanceGoldClient(session=FakeSession())
    assert client.resolve_symbol('XAUT') == 'XAUTUSDT'
    try:
        client.resolve_symbol('GOLD')
    except BinanceGoldError:
        pass
    else:
        raise AssertionError('unsupported asset must fail closed')


def test_metals_block_exposes_separate_buttons_without_fabricating_xauusd():
    client = BinanceGoldClient(session=FakeSession())
    block = build_metals_block(client, '1H', 60)
    assert block['tokens']['PAXG']['ok'] is True
    assert block['tokens']['XAUT']['ok'] is True
    assert block['xauusd']['available'] is False
    assert [b['id'] for b in block['ui']['buttons']] == ['xauusd', 'paxg', 'xaut']
    assert block['policy']['live_execution'] is False


def test_ohlc_validation_rejects_bad_rows():
    client = BinanceGoldClient(session=FakeSession())
    try:
        client._validate([{'timestamp': 2, 'open': 10, 'high': 9, 'low': 8, 'close': 9, 'volume': 1, 'trades': 1}, {'timestamp': 1, 'open': 9, 'high': 10, 'low': 8, 'close': 9, 'volume': 1, 'trades': 1}])
    except BinanceGoldError:
        pass
    else:
        raise AssertionError('invalid OHLC/timestamps must fail closed')
