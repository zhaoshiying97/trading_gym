import pandas as pd
import numpy as np
from trading_gym.envs.portfolio_gym.portfolio_gym import PortfolioTradingGym
import random
import pdb
np.random.seed(64)

def create_mock_data(order_book_ids, start_date="2019-01-01", end_date="2022-01-02", number_feature=3):
    trading_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    number = len(trading_dates) * len(order_book_ids)

    multi_index = pd.MultiIndex.from_product([order_book_ids, trading_dates], names=["order_book_id", "datetime"])
    mock_data = pd.DataFrame(np.random.randn(number, number_feature + 1), index=multi_index,
                             columns=["feature1", "feature2", "feature3", "returns"])
    mock_data["returns"] = mock_data["returns"] / 100  # 当期收益率
    return mock_data


def test_base():
    order_book_ids = ["000001.XSHE"]
    mock_data = create_mock_data(order_book_ids=order_book_ids, start_date="2019-01-01", end_date="2019-01-11")
    sequence_window = 1
    env = PortfolioTradingGym(data_df=mock_data, sequence_window=sequence_window, add_cash=True)
    state = env.reset()
    next_state, reward, done, info = env.step(0.5)
    next_state, reward, done, info = env.step(0.8)  # 正增
    next_state, reward, done, info = env.step(0.4)  # 正减
    next_state, reward, done, info = env.step(1.0)  # 边界
    next_state, reward, done, info = env.step(0.0)  # 边界
    next_state, reward, done, info = env.step(-0.5)
    next_state, reward, done, info = env.step(-0.7)  # 负减
    next_state, reward, done, info = env.step(-0.4)  # 负增
    next_state, reward, done, info = env.step(-1.0)  # 边界
    next_state, reward, done, info = env.step(0.3)  # 跨界
    print(env.experience_buffer["reward"])
    expected_reward = [-0.01033*0.5, 0.017505*0.8, -0.001713*0.4, -0.003866*1.0, 0.005946*0.0, -0.004909*-0.5, -0.000335*-0.7, -0.013583*-0.4, 0.006752*-1.0, 0.007669*0.3]
    print(expected_reward)


def test_one_stock():
    # random test
    order_book_ids = ["000001.XSHE"]
    mock_data = create_mock_data(order_book_ids=order_book_ids, start_date="2019-01-01", end_date="2022-01-02")
    sequence_window = 1
    env = PortfolioTradingGym(data_df=mock_data, sequence_window=sequence_window, add_cash=True)
    state = env.reset()
    actionlist = []

    while True:
        action = random.uniform(-1, 1)
        actionlist.append(action)
        next_state, reward, done, info = env.step(action)
        if done:
            break

    env.render()
    portfolio_reward = np.array(env.experience_buffer["reward"])
    expected_reward = mock_data.xs("000001.XSHE")["returns"].iloc[sequence_window:].values * actionlist

    for i in range(len(actionlist)):
        if actionlist[i] != 0:
            np.testing.assert_almost_equal(portfolio_reward[i], expected_reward[i], decimal=3)
        else:
            np.testing.assert_almost_equal(portfolio_reward[i], info["one_step_fwd_returns"][1], decimal=4)

    return actionlist, portfolio_reward[-1]


def test_one_stock_specificly():
    # specific test
    order_book_ids = ["000001.XSHE"]
    mock_data = create_mock_data(order_book_ids=order_book_ids, start_date="2019-01-01", end_date="2019-07-21")
    sequence_window = 1
    env = PortfolioTradingGym(data_df=mock_data, sequence_window=sequence_window, add_cash=True)
    state = env.reset()
    actionlist = []
    i = 0
    while True:
        action = i/100-1
        actionlist.append(action)
        next_state, reward, done, info = env.step(action)
        if action == 1:
            break
        i += 1
        if done:
            break

    env.render()
    portfolio_reward = np.array(env.experience_buffer["reward"])
    expected_reward = mock_data.xs("000001.XSHE")["returns"].iloc[sequence_window:].values * actionlist

    for i in range(len(actionlist)):
        if actionlist[i] != 0:
            np.testing.assert_almost_equal(portfolio_reward[i], expected_reward[i], decimal=3)
        else:
            np.testing.assert_almost_equal(portfolio_reward[i], info["one_step_fwd_returns"][1], decimal=4)

    return actionlist, portfolio_reward[-1]


if __name__ == "__main__":
    # print(test_one_stock())
    # print(test_one_stock_specificly())
    test_base()

