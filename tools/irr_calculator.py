from flask import request, jsonify

def calculate_irr(principal, payment, periods, n=12, precision=1e-6):
    def npv(rate):
        return sum(payment / (1 + rate/n)**(i+1) for i in range(periods)) - principal
    
    low, high = 0, 1
    while high - low > precision:
        mid = (low + high) / 2
        if npv(mid) > 0:
            low = mid
        else:
            high = mid
    
    return (low + high) / 2

def handle_request():
    try:
        data = request.json
        principal = float(data['principal'])
        payment = float(data['payment'])
        periods = int(data['periods'])

        irr = calculate_irr(principal, payment, periods)
        result = f"真实年化利率 (IRR) 约为: {irr*100:.2f}%"

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400