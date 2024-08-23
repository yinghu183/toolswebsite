import numpy as np
from scipy import optimize
import logging

logging.basicConfig(level=logging.DEBUG)

def calculate_irr(principal, payment, periods):
  """
  计算内部收益率（IRR）
  
  :param principal: 分期本金
  :param payment: 每期还款金额
  :param periods: 还款期数
  :return: 年化IRR
  """
  def npv(rate, cashflows):
      return np.sum(np.array(cashflows) / (1 + rate) ** np.arange(len(cashflows)))

  cashflows = [-principal] + [payment] * periods
  
  try:
      irr = optimize.newton(lambda r: npv(r, cashflows), 0.1)
      annual_irr = (1 + irr) ** 12 - 1  # 假设按月还款，转换为年化利率
      return annual_irr
  except:
      raise ValueError("无法计算IRR，请检查输入数据")

def validate_input(principal, payment, periods):
  """
  验证输入数据
  """
  if principal <= 0 or payment <= 0 or periods <= 0:
      raise ValueError("本金、还款金额和期数必须为正数")
  if payment * periods <= principal:
      raise ValueError("总还款金额必须大于本金")

def calculate_real_irr(principal, payment, periods):
  """
  计算真实分期利率
  
  :param principal: 分期本金
  :param payment: 每期还款金额
  :param periods: 还款期数
  :return: 字典，包含年化IRR和月化IRR
  """
  try:
      validate_input(principal, payment, periods)
      annual_irr = calculate_irr(principal, payment, periods)
      monthly_irr = (1 + annual_irr) ** (1/12) - 1
      
      return {
          "annual_irr": annual_irr,
          "monthly_irr": monthly_irr
      }
  except Exception as e:
      logging.error(f"Error in calculate_real_irr: {str(e)}")
      raise