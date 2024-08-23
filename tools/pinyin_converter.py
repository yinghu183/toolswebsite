# tools/pinyin_converter.py

from pypinyin import lazy_pinyin, Style
import re
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 常见复姓列表，按长度排序以确保优先匹配更长的复姓
COMPOUND_SURNAMES = sorted([
  "欧阳", "太史", "端木", "上官", "司马", "东方", "独孤", "南宫", "万俟", "闻人",
  "夏侯", "诸葛", "尉迟", "公羊", "赫连", "澹台", "皇甫", "宗政", "濮阳", "公冶",
  "太叔", "申屠", "公孙", "慕容", "仲孙", "钟离", "长孙", "宇文", "司徒", "鲜于",
  "司空", "闾丘", "子车", "亓官", "司寇", "巫马", "公西", "颛孙", "壤驷", "公良",
  "漆雕", "乐正", "宰父", "谷梁", "拓跋", "夹谷", "轩辕", "令狐", "段干", "百里",
  "呼延", "东郭", "南门", "羊舌", "微生", "公户", "公玉", "公仪", "梁丘", "公仲",
  "公上", "公门", "公山", "公坚", "左丘", "公伯", "西门", "公祖", "第五", "公乘",
  "贯丘", "公皙", "南荣", "东里", "东宫", "仲长", "子书", "子桑", "即墨", "达奚",
  "褚师", "吴铭"
], key=len, reverse=True)

# 处理常见的多音字
MULTITONE_WORDS = {
  '单': 'Shan',
  '重': 'Chong',
  '任': 'Ren',
  '解': 'Xie',
  '长': 'Chang',
  '乐': 'Yue',
  # 可以根据需要添加更多词汇
}

def convert_to_pinyin(name):
  # 检查是否有复姓
  surname = next((s for s in COMPOUND_SURNAMES if name.startswith(s)), name[0])
  given_name = name[len(surname):]

  # 处理姓氏的多音字情况
  surname_pinyin = MULTITONE_WORDS.get(surname, None)
  if not surname_pinyin:
      surname_pinyin = ''.join([syllable.capitalize() for syllable in lazy_pinyin(surname, style=Style.NORMAL)])
  else:
      surname_pinyin = surname_pinyin.capitalize()

  # 处理名字拼音
  given_name_pinyin = ''.join([syllable.capitalize() for syllable in lazy_pinyin(given_name, style=Style.NORMAL)])

  # 组合姓和名，中间加空格
  return f"{surname_pinyin} {given_name_pinyin}".strip()

def process_names(text):
  try:
      # 使用正则表达式分割输入，支持多种分隔符
      names = re.split(r'[,，\s\n]+', text)
      names = [name.strip() for name in names if name.strip()]
      logging.debug(f"Parsed names: {names}")

      result = []
      for name in names:
          if not name:
              result.append("Error: Empty name")
              continue

          try:
              pinyin_name = convert_to_pinyin(name)
              result.append(pinyin_name)
          except Exception as e:
              logging.error(f"Error converting name '{name}': {str(e)}")
              result.append(f"Error converting {name}: {str(e)}")

      logging.debug(f"Conversion result: {result}")
      return result

  except Exception as e:
      logging.error(f"Unexpected error: {str(e)}")
      return [f"An unexpected error occurred: {str(e)}"]