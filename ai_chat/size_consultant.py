"""
Size Consultant Service - Core size consultation logic
"""

import re
from typing import Dict, List, Optional, Tuple


class SizeConsultant:
    """Chuyên gia tư vấn size với bảng size chuẩn"""
    
    # Bảng size chuẩn từ user
    SIZE_CHART = {
        'ao': {  # Áo Nam/Nữ/Hoodie
            'XS': {'nam': {'cao': (155, 160), 'can': (45, 50)}, 'nu': {'cao': (150, 155), 'can': (40, 45)}, 'note': 'Dáng nhỏ'},
            'S': {'nam': {'cao': (160, 165), 'can': (50, 58)}, 'nu': {'cao': (155, 160), 'can': (45, 50)}, 'note': 'Vừa'},
            'M': {'nam': {'cao': (165, 170), 'can': (58, 65)}, 'nu': {'cao': (160, 165), 'can': (50, 58)}, 'note': 'Chuẩn'},
            'L': {'nam': {'cao': (170, 175), 'can': (65, 73)}, 'nu': {'cao': (165, 170), 'can': (58, 65)}, 'note': 'Thoải mái'},
            'XL': {'nam': {'cao': (175, 180), 'can': (73, 80)}, 'nu': {'cao': (165, 175), 'can': (65, 75)}, 'note': ''},
            'XXL': {'nam': {'cao': (180, 185), 'can': (80, 90)}, 'nu': {'cao': (170, 180), 'can': (75, 85)}, 'note': ''}
        },
        'quan': {  # Quần Nam/Nữ
            'XS': {'vong_eo': (65, 70), 'can': (45, 50), 'so_tuong_duong': '26-27'},
            'S': {'vong_eo': (70, 75), 'can': (50, 58), 'so_tuong_duong': '28'},
            'M': {'vong_eo': (75, 80), 'can': (58, 65), 'so_tuong_duong': '29-30'},
            'L': {'vong_eo': (80, 85), 'can': (65, 73), 'so_tuong_duong': '31-32'},
            'XL': {'vong_eo': (85, 90), 'can': (73, 80), 'so_tuong_duong': '33-34'},
            'XXL': {'vong_eo': (90, 100), 'can': (80, 90), 'so_tuong_duong': '35-36'}
        },
        'dam_vay': {  # Đầm/Váy
            'XS': {'vong_nguc': (78, 82), 'vong_eo': (60, 65), 'can': (40, 45)},
            'S': {'vong_nguc': (83, 86), 'vong_eo': (66, 69), 'can': (45, 50)},
            'M': {'vong_nguc': (87, 90), 'vong_eo': (70, 74), 'can': (50, 58)},
            'L': {'vong_nguc': (91, 95), 'vong_eo': (75, 79), 'can': (58, 65)},
            'XL': {'vong_nguc': (96, 100), 'vong_eo': (80, 84), 'can': (65, 75)}
        },
        'giay': {  # Giày/Dép
            36: {'chieu_dai': 22.5, 'nu_eu': 36},
            37: {'chieu_dai': 23.0, 'nu_eu': 37},
            38: {'chieu_dai': 23.5, 'nam_eu': 38, 'nu_eu': 38},
            39: {'chieu_dai': 24.5, 'nam_eu': 39, 'nu_eu': 39},
            40: {'chieu_dai': 25.0, 'nam_eu': 40, 'nu_eu': 40},
            41: {'chieu_dai': 25.5, 'nam_eu': 41, 'nu_eu': 41},
            42: {'chieu_dai': 26.0, 'nam_eu': 42},
            43: {'chieu_dai': 26.5, 'nam_eu': 43},
            44: {'chieu_dai': 27.0, 'nam_eu': 44},
            45: {'chieu_dai': 27.5, 'nam_eu': 45}
        }
    }
    
    def extract_measurements(self, message: str) -> Dict:
        """Trích xuất thông tin đo lường từ message"""
        measurements = {}
        
        # Chiều cao (1m56, 1.56m, 156cm, etc.)
        height_patterns = [
            r'(\d+)m(\d+)',  # 1m56
            r'(\d+)\.(\d+)m',  # 1.56m  
            r'(\d+)cm',  # 156cm
            r'cao\s*(\d+)',  # cao 156
        ]
        
        for pattern in height_patterns:
            match = re.search(pattern, message)
            if match:
                if 'm' in pattern and len(match.groups()) == 2:
                    # 1m56 -> 156cm
                    measurements['height'] = int(match.group(1)) * 100 + int(match.group(2))
                elif '.' in pattern:
                    # 1.56m -> 156cm
                    measurements['height'] = int(float(match.group(1) + '.' + match.group(2)) * 100)
                else:
                    # 156cm hoặc cao 156
                    measurements['height'] = int(match.group(1))
                break
        
        # Cân nặng
        weight_patterns = [
            r'(\d+)kg',
            r'nặng\s*(\d+)',
            r'cân\s*(\d+)'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, message)
            if match:
                measurements['weight'] = int(match.group(1))
                break
        
        # Giới tính
        if any(word in message.lower() for word in ['nam', 'boy', 'men', 'anh', 'chú']):
            measurements['gender'] = 'nam'
        elif any(word in message.lower() for word in ['nữ', 'girl', 'women', 'chị', 'cô']):
            measurements['gender'] = 'nu'
        else:
            measurements['gender'] = 'unisex'  # Default
            
        return measurements
    
    def detect_product_type(self, message: str) -> str:
        """Phát hiện loại sản phẩm từ message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['áo', 'hoodie', 'sweater', 'shirt']):
            return 'ao'
        elif any(word in message_lower for word in ['quần', 'jean', 'jogger', 'pants']):
            return 'quan'
        elif any(word in message_lower for word in ['đầm', 'váy', 'dress', 'skirt']):
            return 'dam_vay'
        elif any(word in message_lower for word in ['giày', 'dép', 'shoes', 'sandal']):
            return 'giay'
        else:
            return 'ao'  # Default to áo
    
    def recommend_size(self, measurements: Dict, product_type: str) -> Dict:
        """Gợi ý size dựa trên measurements và product type"""
        if not measurements.get('height') or not measurements.get('weight'):
            return {
                'success': False,
                'message': 'Cần thông tin chiều cao và cân nặng để tư vấn size chính xác.'
            }
        
        height = measurements['height']
        weight = measurements['weight']
        gender = measurements.get('gender', 'unisex')
        
        if product_type == 'giay':
            return self._recommend_shoe_size(height, weight)
        
        chart = self.SIZE_CHART.get(product_type, self.SIZE_CHART['ao'])
        recommended_sizes = []
        
        for size, data in chart.items():
            if product_type in ['ao']:
                # Try specific gender first, then fallback to both genders
                genders_to_check = [gender] if gender in ['nam', 'nu'] else ['nam', 'nu']

                for check_gender in genders_to_check:
                    if check_gender in data:
                        size_data = data[check_gender]
                        height_range = size_data['cao']
                        weight_range = size_data['can']

                        if (height_range[0] <= height <= height_range[1] and
                            weight_range[0] <= weight <= weight_range[1]):
                            recommended_sizes.append({
                                'size': size,
                                'note': data.get('note', ''),
                                'fit': 'perfect',
                                'gender_used': check_gender
                            })
                            break  # Found perfect fit, no need to check other gender
                        elif (height_range[0] - 5 <= height <= height_range[1] + 5 and
                              weight_range[0] - 5 <= weight <= weight_range[1] + 5):
                            recommended_sizes.append({
                                'size': size,
                                'note': data.get('note', ''),
                                'fit': 'acceptable',
                                'gender_used': check_gender
                            })
            
            elif product_type in ['quan', 'dam_vay']:
                weight_range = data['can']
                if weight_range[0] <= weight <= weight_range[1]:
                    recommended_sizes.append({
                        'size': size,
                        'fit': 'perfect'
                    })
        
        if not recommended_sizes:
            # Check if measurements are way outside normal ranges
            if self._is_outside_normal_range(height, weight, product_type):
                return {
                    'success': False,
                    'message': f'Với chiều cao {height}cm và cân nặng {weight}kg, bạn nằm ngoài bảng size chuẩn. Vui lòng liên hệ trực tiếp để được tư vấn size phù hợp nhất.',
                    'special_case': True
                }

            # Find closest size if no perfect match
            closest_size = self._find_closest_size(height, weight, product_type, gender)
            if closest_size:
                return {
                    'success': True,
                    'recommended_sizes': [closest_size],
                    'measurements': measurements,
                    'product_type': product_type,
                    'note': 'Size được gợi ý dựa trên khoảng cách gần nhất với bảng size chuẩn. Nên thử trước khi mua.'
                }
            else:
                return {
                    'success': False,
                    'message': f'Không tìm thấy size phù hợp cho chiều cao {height}cm, cân nặng {weight}kg. Vui lòng liên hệ để tư vấn thêm.'
                }
        
        # Ưu tiên size perfect fit
        perfect_fits = [s for s in recommended_sizes if s['fit'] == 'perfect']
        if perfect_fits:
            recommended_sizes = perfect_fits
        
        return {
            'success': True,
            'recommended_sizes': recommended_sizes,
            'measurements': measurements,
            'product_type': product_type
        }
    
    def _recommend_shoe_size(self, height: int, weight: int) -> Dict:
        """Gợi ý size giày dựa trên chiều cao (ước tính)"""
        # Ước tính chiều dài chân từ chiều cao (công thức gần đúng)
        estimated_foot_length = height * 0.15  # Khoảng 15% chiều cao
        
        best_size = None
        min_diff = float('inf')
        
        for size, data in self.SIZE_CHART['giay'].items():
            diff = abs(data['chieu_dai'] - estimated_foot_length)
            if diff < min_diff:
                min_diff = diff
                best_size = size
        
        return {
            'success': True,
            'recommended_sizes': [{'size': best_size, 'fit': 'estimated'}],
            'note': 'Size giày được ước tính từ chiều cao. Nên đo chân chính xác để chọn size tốt nhất.',
            'estimated_foot_length': round(estimated_foot_length, 1)
        }

    def _find_closest_size(self, height: int, weight: int, product_type: str, gender: str) -> Optional[Dict]:
        """Tìm size gần nhất khi không có perfect match"""
        if product_type not in ['ao', 'quan', 'dam_vay']:
            return None

        chart = self.SIZE_CHART[product_type]
        best_size = None
        min_distance = float('inf')

        for size, data in chart.items():
            if product_type == 'ao':
                # Try specific gender first, then fallback to both genders
                genders_to_check = [gender] if gender in ['nam', 'nu'] else ['nam', 'nu']

                for check_gender in genders_to_check:
                    if check_gender in data:
                        size_data = data[check_gender]
                        height_range = size_data['cao']
                        weight_range = size_data['can']

                        # Calculate distance from ranges
                        height_dist = min(abs(height - height_range[0]), abs(height - height_range[1]))
                        if height_range[0] <= height <= height_range[1]:
                            height_dist = 0

                        weight_dist = min(abs(weight - weight_range[0]), abs(weight - weight_range[1]))
                        if weight_range[0] <= weight <= weight_range[1]:
                            weight_dist = 0

                        # Combined distance (weighted)
                        total_distance = height_dist * 0.6 + weight_dist * 0.4

                        if total_distance < min_distance:
                            min_distance = total_distance
                            best_size = {
                                'size': size,
                                'fit': 'closest',
                                'note': data.get('note', ''),
                                'distance': round(total_distance, 1),
                                'gender_used': check_gender
                            }

            elif product_type in ['quan', 'dam_vay']:
                weight_range = data['can']
                weight_dist = min(abs(weight - weight_range[0]), abs(weight - weight_range[1]))
                if weight_range[0] <= weight <= weight_range[1]:
                    weight_dist = 0

                if weight_dist < min_distance:
                    min_distance = weight_dist
                    best_size = {
                        'size': size,
                        'fit': 'closest',
                        'distance': round(weight_dist, 1)
                    }

        return best_size

    def _is_outside_normal_range(self, height: int, weight: int, product_type: str) -> bool:
        """Kiểm tra xem measurements có nằm quá xa bảng size không"""
        if product_type not in ['ao', 'quan', 'dam_vay']:
            return False

        chart = self.SIZE_CHART[product_type]

        if product_type == 'ao':
            # Tìm range lớn nhất và nhỏ nhất
            min_height = min_weight = float('inf')
            max_height = max_weight = 0

            for size_data in chart.values():
                for gender_data in ['nam', 'nu']:
                    if gender_data in size_data:
                        data = size_data[gender_data]
                        height_range = data['cao']
                        weight_range = data['can']

                        min_height = min(min_height, height_range[0])
                        max_height = max(max_height, height_range[1])
                        min_weight = min(min_weight, weight_range[0])
                        max_weight = max(max_weight, weight_range[1])

            # Đặc biệt nghiêm ngặt với trường hợp cân nặng quá cao
            if weight > max_weight + 5:  # Quá 5kg so với max weight trong bảng
                return True

            # Trường hợp đặc biệt: chiều cao quá thấp với cân nặng cao
            if height < 155 and weight > 70:  # Người thấp nhưng nặng (tăng độ strict)
                return True

            # Trường hợp đặc biệt: chiều cao thấp với cân nặng rất cao
            if height < 160 and weight > 75:  # Mở rộng case
                return True

            # Kiểm tra nếu quá xa (>10cm hoặc >8kg từ range)
            height_outside = height < (min_height - 10) or height > (max_height + 10)
            weight_outside = weight < (min_weight - 8) or weight > (max_weight + 5)

            return height_outside or weight_outside  # OR thay vì AND

        elif product_type in ['quan', 'dam_vay']:
            # Tương tự cho quần và đầm
            max_weight = max(data['can'][1] for data in chart.values())
            min_weight = min(data['can'][0] for data in chart.values())

            return weight > max_weight + 10 or weight < min_weight - 10

        return False


# Global instance
size_consultant = SizeConsultant()
