from scipy.optimize import minimize
import random
def gradient_descent_minimize(goal, m_lb, m_ub, constraints, options):
    """
    :param goal: 目标函数
    :param m_lb: 参数下界
    :param m_ub: 参数上界
    :param constraints: 约束
    :param options: 优化设置
    :return: 最佳结果
    该函数为梯度优化器，会使用随机值进行10次模拟，一旦有一次的损失函数达到目标值，就退出循环
    """
    res_list = []

    bounds = []
    for i in range(len(m_lb)):
        bounds.append([m_lb[i], m_ub[i]])

    for j in range(10):
        initial_value_list = []
        for i in range(len(m_lb)):
            initial_value = random.uniform(m_lb[i], m_ub[i])
            initial_value_list.append(initial_value)
        print(bounds)
        result = minimize(fun=goal, x0=initial_value_list, constraints=constraints, bounds=bounds, method='SLSQP',
                          options=options)
        res_list.append(result)
        if result.fun < 0.05:
            break

    result = min(res_list, key=lambda result: result.fun)
    return result
