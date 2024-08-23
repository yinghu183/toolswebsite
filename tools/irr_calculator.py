# tools/irr_calculator.py

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
  try:
      # 创建现金流数组，第一个元素为负的本金（表示初始投资）
      cashflows = [-principal] + [payment] * periods
      
      # 使用numpy的irr函数计算内部收益率
      irr = np.irr(cashflows)
      
      # 将月度IRR转换为年化IRR
      annual_irr = (1 + irr)**12 - 1
      
      logging.debug(f"Calculated IRR: {annual_irr}")
      return annual_irr
  except Exception as e:
      logging.error(f"Error calculating IRR: {str(e)}")
      raise

def validate_input(principal, payment, periods):
  """
  验证输入数据
  """
  if principal <= 0 or payment <= 0 or periods <= 0:
      raise ValueError("Principal, payment, and periods must be positive numbers.")
  if payment * periods <= principal:
      raise ValueError("Total payments must be greater than the principal.")

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
      monthly_irr = (1 + annual_irr)**(1/12) - 1
      
      return {
          "annual_irr": annual_irr,
          "monthly_irr": monthly_irr
      }
  except Exception as e:
      logging.error(f"Error in calculate_real_irr: {str(e)}")
      raise