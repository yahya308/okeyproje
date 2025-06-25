import numpy as np
from collections import defaultdict, Counter
import random
from typing import List, Dict, Tuple, Optional
import json
import itertools

class OkeyAI:
    def __init__(self):
        self.colors = ['kirmizi', 'sari', 'mavi', 'siyah']
        self.numbers = list(range(1, 14))  # 1-13
        self.all_tiles = self._generate_all_tiles()
        
    def _generate_all_tiles(self) -> List[Dict]:
        """Tüm taşları oluştur"""
        tiles = []
        for color in self.colors:
            for number in self.numbers:
                # Her sayıdan her renkten 2 adet
                for _ in range(2):
                    tiles.append({
                        'color': color,
                        'number': number,
                        'id': f"{color}_{number}_{_}"
                    })
        # 2 adet sahte okey ekle
        for i in range(2):
            tiles.append({
                'color': 'sahte_okey',
                'number': 0,
                'id': f"sahte_okey_{i}"
            })
        return tiles
    
    def _get_okey_value(self, indicator_tile: Dict) -> Dict:
        """Gösterge taşına göre okey taşının değerini hesapla"""
        if indicator_tile['number'] == 13:
            # 13'ten sonra 1'e döner
            okey_number = 1
        else:
            okey_number = indicator_tile['number'] + 1
            
        return {
            'color': indicator_tile['color'],
            'number': okey_number,
            'is_okey': True
        }
    
    def _calculate_per_score(self, per: List[Dict]) -> int:
        """Per puanını hesapla"""
        if len(per) < 3:
            return 0
            
        # Aynı renk ardışık sayılar
        if len(set(tile['color'] for tile in per)) == 1:
            numbers = sorted([tile['number'] for tile in per])
            if numbers == list(range(numbers[0], numbers[0] + len(numbers))):
                return sum(numbers)
        
        # Farklı renkler aynı sayı
        if len(set(tile['number'] for tile in per)) == 1:
            return per[0]['number'] * len(per)
            
        return 0
    
    def _is_valid_per(self, per: List[Dict]) -> bool:
        """Per geçerli mi kontrol et"""
        if len(per) < 3:
            return False
            
        # Aynı renk ardışık sayılar
        if len(set(tile['color'] for tile in per)) == 1:
            numbers = sorted([tile['number'] for tile in per])
            # 12-13-1 geçersiz
            if 12 in numbers and 13 in numbers and 1 in numbers:
                return False
            return numbers == list(range(numbers[0], numbers[0] + len(numbers)))
        
        # Farklı renkler aynı sayı
        if len(set(tile['number'] for tile in per)) == 1:
            return True
            
        return False
    
    def _find_sequential_pers(self, tiles: List[Dict]) -> List[List[Dict]]:
        """Aynı renk ardışık sayı perlerini bul (optimize edilmiş)"""
        pers = []
        
        # Renklere göre grupla
        color_groups = defaultdict(list)
        for tile in tiles:
            color_groups[tile['color']].append(tile)
        
        # Her renk için ardışık perler bul
        for color, color_tiles in color_groups.items():
            numbers = sorted([t['number'] for t in color_tiles])
            
            # 3'lü ardışık kombinasyonlar
            for i in range(len(numbers) - 2):
                for j in range(i + 2, len(numbers)):
                    seq = numbers[i:j+1]
                    if len(seq) >= 3 and seq == list(range(seq[0], seq[0] + len(seq))):
                        # Bu sayıları içeren taşları bul
                        per_tiles = []
                        for num in seq:
                            matching_tiles = [t for t in color_tiles if t['number'] == num]
                            if matching_tiles:
                                per_tiles.append(matching_tiles[0])
                        if len(per_tiles) >= 3:
                            pers.append(per_tiles)
        
        return pers
    
    def _find_same_number_pers(self, tiles: List[Dict]) -> List[List[Dict]]:
        """Aynı sayı farklı renk perlerini bul (optimize edilmiş)"""
        pers = []
        
        # Sayılara göre grupla
        number_groups = defaultdict(list)
        for tile in tiles:
            number_groups[tile['number']].append(tile)
        
        # Her sayı için farklı renk kombinasyonları
        for number, number_tiles in number_groups.items():
            if len(number_tiles) >= 3:
                # 3'lü ve 4'lü kombinasyonlar
                for size in [3, 4]:
                    if len(number_tiles) >= size:
                        for combo in itertools.combinations(number_tiles, size):
                            # Farklı renkler mi kontrol et
                            colors = [t['color'] for t in combo]
                            if len(set(colors)) == len(colors):  # Tüm renkler farklı
                                pers.append(list(combo))
        
        return pers
    
    def _find_all_pers_optimized(self, tiles: List[Dict]) -> List[List[Dict]]:
        """Optimize edilmiş per bulma algoritması"""
        pers = []
        
        # Ardışık perler
        sequential_pers = self._find_sequential_pers(tiles)
        pers.extend(sequential_pers)
        
        # Aynı sayı perler
        same_number_pers = self._find_same_number_pers(tiles)
        pers.extend(same_number_pers)
        
        return pers
    
    def _find_all_pers_with_okey(self, tiles: List[Dict], okey_tile: Optional[Dict] = None) -> List[List[Dict]]:
        """Okey taşı dahil tüm geçerli perleri bul (optimize edilmiş)"""
        if not okey_tile:
            return self._find_all_pers_optimized(tiles)
        
        # Okey taşını bul
        okey_tiles = [t for t in tiles if t.get('is_okey') or t['color'] == 'sahte_okey']
        normal_tiles = [t for t in tiles if not t.get('is_okey') and t['color'] != 'sahte_okey']
        
        if not okey_tiles:
            return self._find_all_pers_optimized(tiles)
        
        pers = []
        okey_value = self._get_okey_value(okey_tile)
        
        # Okey taşını joker olarak kullanarak perler oluştur
        for okey in okey_tiles:
            # Okey taşını en yararlı olabileceği yerlerde dene
            useful_positions = self._find_useful_okey_positions(normal_tiles, okey_value)
            
            for position in useful_positions:
                temp_tiles = normal_tiles.copy()
                temp_okey = {
                    'color': position['color'],
                    'number': position['number'],
                    'is_okey': True,
                    'original_okey': okey
                }
                temp_tiles.append(temp_okey)
                
                # Bu kombinasyonla perler bul
                temp_pers = self._find_all_pers_optimized(temp_tiles)
                for per in temp_pers:
                    # Perde okey taşını gerçek değeriyle değiştir
                    final_per = []
                    for tile in per:
                        if tile.get('is_okey'):
                            final_per.append(okey)
                        else:
                            final_per.append(tile)
                    pers.append(final_per)
        
        # Normal perleri de ekle
        normal_pers = self._find_all_pers_optimized(normal_tiles)
        pers.extend(normal_pers)
        
        return pers
    
    def _find_useful_okey_positions(self, tiles: List[Dict], okey_value: Dict) -> List[Dict]:
        """Okey taşının en yararlı olabileceği pozisyonları bul"""
        positions = []
        
        # Mevcut taşları analiz et
        color_groups = defaultdict(list)
        number_groups = defaultdict(list)
        
        for tile in tiles:
            color_groups[tile['color']].append(tile['number'])
            number_groups[tile['number']].append(tile['color'])
        
        # Ardışık seriler için uygun pozisyonlar
        for color, numbers in color_groups.items():
            numbers = sorted(numbers)
            for i in range(len(numbers) - 1):
                if numbers[i+1] - numbers[i] == 2:  # Arada bir sayı eksik
                    positions.append({
                        'color': color,
                        'number': numbers[i] + 1
                    })
        
        # Aynı sayı serileri için uygun pozisyonlar
        for number, colors in number_groups.items():
            if len(colors) == 2:  # 2 renk varsa, 3. renk eklenebilir
                missing_colors = [c for c in self.colors if c not in colors]
                for color in missing_colors:
                    positions.append({
                        'color': color,
                        'number': number
                    })
        
        # Eğer hiç uygun pozisyon bulunamazsa, okey'in kendi değerini kullan
        if not positions:
            positions.append(okey_value)
        
        return positions[:10]  # En fazla 10 pozisyon dene
    
    def _find_best_arrangement(self, tiles: List[Dict], okey_tile: Optional[Dict] = None) -> Dict:
        """En iyi taş dizilimini bul (optimize edilmiş)"""
        # Okey taşını işle
        processed_tiles = self._process_okey_tiles(tiles, okey_tile)
        
        # Tüm perleri bul
        all_pers = self._find_all_pers_with_okey(processed_tiles, okey_tile)
        
        if not all_pers:
            return {
                'pers': [],
                'score': 0,
                'unused_tiles': processed_tiles,
                'total_tiles_used': 0
            }
        
        # En yüksek puanlı kombinasyonu bul (greedy algoritma)
        best_score = 0
        best_arrangement = []
        best_unused = processed_tiles.copy()
        
        # Perleri puana göre sırala
        pers_with_scores = [(per, self._calculate_per_score(per)) for per in all_pers]
        pers_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        used_tiles = set()
        current_pers = []
        
        for per, score in pers_with_scores:
            # Bu per kullanılabilir mi kontrol et
            per_tiles = set()
            for tile in per:
                tile_id = f"{tile['color']}_{tile['number']}"
                per_tiles.add(tile_id)
            
            # Çakışma var mı kontrol et
            if not per_tiles.intersection(used_tiles):
                current_pers.append(per)
                used_tiles.update(per_tiles)
        
        # Toplam puanı hesapla
        total_score = sum(self._calculate_per_score(per) for per in current_pers)
        
        # Kullanılmayan taşları bul
        unused_tiles = []
        for tile in processed_tiles:
            tile_id = f"{tile['color']}_{tile['number']}"
            if tile_id not in used_tiles:
                unused_tiles.append(tile)
        
        return {
            'pers': current_pers,
            'score': total_score,
            'unused_tiles': unused_tiles,
            'total_tiles_used': len(processed_tiles) - len(unused_tiles)
        }
    
    def _process_okey_tiles(self, tiles: List[Dict], okey_tile: Optional[Dict] = None) -> List[Dict]:
        """Okey taşlarını işle"""
        if not okey_tile:
            return tiles
        
        processed_tiles = []
        okey_value = self._get_okey_value(okey_tile)
        
        for tile in tiles:
            if tile['color'] == 'sahte_okey':
                # Sahte okey'i gerçek okey değeriyle değiştir
                processed_tiles.append({
                    'color': okey_value['color'],
                    'number': okey_value['number'],
                    'is_okey': True,
                    'original': tile
                })
            else:
                processed_tiles.append(tile)
        
        return processed_tiles
    
    def _calculate_tile_value(self, tile: Dict, player_tiles: List[Dict], 
                            discarded_tiles: List[Dict], okey_tile: Optional[Dict] = None) -> float:
        """Taşın değerini hesapla"""
        value = 0
        
        # Okey taşını işle
        if tile['color'] == 'sahte_okey' and okey_tile:
            okey_value = self._get_okey_value(okey_tile)
            tile = {
                'color': okey_value['color'],
                'number': okey_value['number'],
                'is_okey': True
            }
        
        # Temel değer
        if tile.get('is_okey'):
            value += 50  # Okey taşı çok değerli
        else:
            value += tile['number']
        
        # Diğer oyuncuların attığı taşlarla uyumluluk
        for discarded in discarded_tiles:
            if discarded['color'] == tile['color'] and discarded['number'] == tile['number']:
                value -= 5  # Aynı taş atılmış, değeri düşük
        
        # Oyuncunun elindeki taşlarla uyumluluk
        for player_tile in player_tiles:
            if player_tile['color'] == tile['color']:
                if abs(player_tile['number'] - tile['number']) == 1:
                    value += 3  # Ardışık sayı
                elif player_tile['number'] == tile['number']:
                    value += 2  # Aynı sayı
        
        return value
    
    def _predict_opponent_tiles(self, discarded_tiles: List[Dict], 
                              player_tiles: List[Dict], okey_tile: Optional[Dict] = None) -> Dict:
        """Rakip taşlarını tahmin et"""
        all_tiles = self.all_tiles.copy()
        
        # Oyuncunun taşlarını çıkar
        for tile in player_tiles:
            all_tiles = [t for t in all_tiles if not (
                t['color'] == tile['color'] and t['number'] == tile['number']
            )]
        
        # Atılan taşları çıkar
        for tile in discarded_tiles:
            all_tiles = [t for t in all_tiles if not (
                t['color'] == tile['color'] and t['number'] == tile['number']
            )]
        
        # Okey taşını çıkar (eğer varsa)
        if okey_tile:
            okey_value = self._get_okey_value(okey_tile)
            all_tiles = [t for t in all_tiles if not (
                t['color'] == okey_value['color'] and t['number'] == okey_value['number']
            )]
        
        # Kalan taşları rastgele dağıt
        random.shuffle(all_tiles)
        
        opponent_tiles = all_tiles[:39]  # 3 rakip × 13 taş
        
        return {
            'opponent1': opponent_tiles[:13],
            'opponent2': opponent_tiles[13:26],
            'opponent3': opponent_tiles[26:39],
            'remaining_deck': opponent_tiles[39:]
        }
    
    def analyze_hand(self, player_tiles: List[Dict], 
                    discarded_tiles: Optional[List[Dict]] = None,
                    okey_tile: Optional[Dict] = None) -> Dict:
        """Eli analiz et (optimize edilmiş)"""
        if discarded_tiles is None:
            discarded_tiles = []
        
        # En iyi dizilimi bul
        arrangement = self._find_best_arrangement(player_tiles, okey_tile)
        
        # Her taşın değerini hesapla (sadece kullanılmayan taşlar için)
        tile_values = {}
        for tile in arrangement['unused_tiles']:
            tile_values[f"{tile['color']}_{tile['number']}"] = self._calculate_tile_value(
                tile, player_tiles, discarded_tiles, okey_tile
            )
        
        # Rakip tahminleri (basitleştirilmiş)
        opponent_prediction = {
            'opponent1': [],
            'opponent2': [],
            'opponent3': [],
            'remaining_deck': []
        }
        
        # Risk analizi
        risk_analysis = self._analyze_risks(player_tiles, discarded_tiles, arrangement, okey_tile)
        
        return {
            'best_arrangement': arrangement,
            'tile_values': tile_values,
            'opponent_prediction': opponent_prediction,
            'risk_analysis': risk_analysis,
            'recommendations': self._generate_recommendations(arrangement, tile_values, risk_analysis, okey_tile)
        }
    
    def _analyze_risks(self, player_tiles: List[Dict], 
                      discarded_tiles: List[Dict],
                      arrangement: Dict,
                      okey_tile: Optional[Dict] = None) -> Dict:
        """Risk analizi yap"""
        risks = {}
        
        # Kullanılmayan taşların riski
        for tile in arrangement['unused_tiles']:
            risk_score = 0
            
            # Okey taşı özel değerlendirme
            if tile.get('is_okey') or tile['color'] == 'sahte_okey':
                risk_score += 15  # Okey taşını atmak çok riskli
            else:
                # Diğer oyuncuların atıp atmadığına bak
                discarded_count = sum(1 for t in discarded_tiles 
                                    if t['color'] == tile['color'] and t['number'] == tile['number'])
                
                if discarded_count >= 2:
                    risk_score += 10  # Çok riskli
                elif discarded_count == 1:
                    risk_score += 5   # Orta risk
                else:
                    risk_score += 2   # Düşük risk
            
            risks[f"{tile['color']}_{tile['number']}"] = risk_score
        
        return risks
    
    def _generate_recommendations(self, arrangement: Dict, 
                                tile_values: Dict, 
                                risk_analysis: Dict,
                                okey_tile: Optional[Dict] = None) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # Puan önerisi
        if arrangement['score'] >= 101:
            recommendations.append(f"✅ El açabilirsiniz! Puan: {arrangement['score']}")
        else:
            needed = 101 - arrangement['score']
            recommendations.append(f"⚠️ El açmak için {needed} puan daha gerekli")
        
        # Okey taşı önerisi
        if okey_tile:
            okey_value = self._get_okey_value(okey_tile)
            recommendations.append(f"🎯 Bu elde Okey taşı: {okey_value['color']} {okey_value['number']}")
        
        # Taş önerisi
        if arrangement['unused_tiles']:
            best_tile_to_discard = min(arrangement['unused_tiles'], 
                                     key=lambda t: tile_values.get(f"{t['color']}_{t['number']}", 0))
            recommendations.append(f"🎯 Atılacak en iyi taş: {best_tile_to_discard['color']} {best_tile_to_discard['number']}")
        
        # Risk uyarıları
        high_risk_tiles = [tile for tile, risk in risk_analysis.items() if risk > 7]
        if high_risk_tiles:
            recommendations.append(f"⚠️ Yüksek riskli taşlar: {', '.join(high_risk_tiles)}")
        
        return recommendations
    
    def monte_carlo_simulation(self, player_tiles: List[Dict],
                             discarded_tiles: Optional[List[Dict]] = None,
                             okey_tile: Optional[Dict] = None,
                             num_simulations: int = 100) -> Dict:
        """Monte Carlo simülasyonu (optimize edilmiş)"""
        if discarded_tiles is None:
            discarded_tiles = []
        
        results = {
            'win_rate': 0,
            'avg_score': 0,
            'best_moves': [],
            'risk_assessment': {}
        }
        
        wins = 0
        total_score = 0
        move_scores = defaultdict(list)
        
        # Simülasyon sayısını azalt
        for _ in range(min(num_simulations, 100)):
            # Rastgele taş dağılımı
            simulation = self._simulate_single_game(player_tiles, discarded_tiles, okey_tile)
            
            if simulation['won']:
                wins += 1
            
            total_score += simulation['score']
            
            # Hamle skorlarını kaydet
            for move, score in simulation['move_scores'].items():
                move_scores[move].append(score)
        
        # Sonuçları hesapla
        if num_simulations > 0:
            results['win_rate'] = wins / num_simulations
            results['avg_score'] = total_score / num_simulations
        
        # En iyi hamleleri bul
        for move, scores in move_scores.items():
            if scores:
                avg_score = np.mean(scores)
                results['best_moves'].append({
                    'move': move,
                    'avg_score': avg_score,
                    'win_rate': sum(1 for s in scores if s > 0) / len(scores)
                })
        
        # En iyi hamleleri sırala
        results['best_moves'].sort(key=lambda x: x['avg_score'], reverse=True)
        
        return results
    
    def _simulate_single_game(self, player_tiles: List[Dict],
                            discarded_tiles: List[Dict],
                            okey_tile: Optional[Dict] = None) -> Dict:
        """Tek oyun simülasyonu"""
        # Oyuncunun hamlelerini simüle et
        arrangement = self._find_best_arrangement(player_tiles, okey_tile)
        
        # Kullanılmayan taşları değerlendir
        move_scores = {}
        for tile in arrangement['unused_tiles']:
            # Bu taşı atarsak ne olur simülasyonu
            remaining_tiles = [t for t in player_tiles if t != tile]
            new_arrangement = self._find_best_arrangement(remaining_tiles, okey_tile)
            move_scores[f"{tile['color']}_{tile['number']}"] = new_arrangement['score']
        
        return {
            'won': arrangement['score'] >= 101,
            'score': arrangement['score'],
            'move_scores': move_scores
        }
    
    def suggest_best_tile(self, player_tiles: List[Dict],
                         discarded_tiles: Optional[List[Dict]] = None,
                         okey_tile: Optional[Dict] = None) -> Dict:
        """En iyi atılacak taşı öner"""
        if discarded_tiles is None:
            discarded_tiles = []
        
        # Mevcut durumu analiz et
        analysis = self.analyze_hand(player_tiles, discarded_tiles, okey_tile)
        
        # Kullanılmayan taşları değerlendir
        unused_tiles = analysis['best_arrangement']['unused_tiles']
        
        if not unused_tiles:
            return {
                'suggestion': 'Tüm taşlar kullanılıyor, el açabilirsiniz!',
                'tile': None,
                'reason': 'Mükemmel el dizilimi'
            }
        
        # En düşük değerli taşı bul
        best_tile_to_discard = min(unused_tiles, 
                                 key=lambda t: analysis['tile_values'].get(f"{t['color']}_{t['number']}", 0))
        
        # Risk analizi
        risk = analysis['risk_analysis'].get(f"{best_tile_to_discard['color']}_{best_tile_to_discard['number']}", 0)
        
        tile_value = analysis['tile_values'].get(f"{best_tile_to_discard['color']}_{best_tile_to_discard['number']}", 0)
        reason = f"En düşük değerli taş (değer: {tile_value:.1f})"
        
        # Okey taşı özel uyarısı
        if best_tile_to_discard.get('is_okey') or best_tile_to_discard['color'] == 'sahte_okey':
            reason += ", OKEY TAŞI - Çok dikkatli olun!"
        
        if risk > 7:
            reason += f", Yüksek risk ({risk})"
        elif risk > 4:
            reason += f", Orta risk ({risk})"
        else:
            reason += f", Düşük risk ({risk})"
        
        return {
            'suggestion': f"{best_tile_to_discard['color']} {best_tile_to_discard['number']} atın",
            'tile': best_tile_to_discard,
            'reason': reason,
            'risk_level': risk
        } 