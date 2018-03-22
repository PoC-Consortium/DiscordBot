import grpc
import api_pb2
import api_pb2_grpc
import config_loader as config

def get_pool_stats(pool_name='0-100-pool.burst.cryptoguru.org:8008'):
    """
    gets pool statistics
    """
    channel = grpc.insecure_channel(pool_name)
    stub = api_pb2_grpc.ApiStub(channel)
    pool_stats = stub.GetPoolStatsInfo(api_pb2.Void())
    block_info = stub.GetBlockInfo(api_pb2.Void())
    return pool_stats


def get_block_info(pool_name='0-100-pool.burst.cryptoguru.org:8008'):
    """
    gets statistics about current block
    """
    channel = grpc.insecure_channel(pool_name)
    stub = api_pb2_grpc.ApiStub(channel)
    block_info = stub.GetBlockInfo(api_pb2.Void())
    return block_info


def get_miner_stats(miner_id):
    for pool in config.POOL_URL.values():
        channel = grpc.insecure_channel(pool)
        stub = api_pb2_grpc.ApiStub(channel)
        try:
            miner = stub.GetMinerInfo(api_pb2.MinerRequest(ID=miner_id))
        except:
            not_found = (None, None)
            continue
        return (miner, pool)
    return not_found


if __name__ == '__main__':
    test_pool_name = '0-100-pool.burst.cryptoguru.org:8008'
    test_miner_id = 4727314633861519997
    print("~ POOL STATISTICS ~")
    print(get_pool_stats(test_pool_name))
    print("~ BLOCK INFO ~")
    print(get_block_info(test_pool_name))
    print("~ MINER INFO ~")
    print(get_miner_stats(test_miner_id))
