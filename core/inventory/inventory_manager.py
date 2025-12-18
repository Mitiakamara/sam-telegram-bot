# sam-telegram-bot/core/inventory/inventory_manager.py
"""
Gestor de inventario con soporte conversacional.
Detecta intenciones como "mi inventario", "uso pocion", "agarro espada".
"""
import re
import logging
from typing import Optional, Dict, Any, Tuple
from .starting_equipment import format_inventory_display

logger = logging.getLogger(__name__)


class InventoryManager:
    """Gestiona el inventario de personajes de forma conversacional."""
    
    # Patrones para detectar consultas de inventario
    INVENTORY_PATTERNS = [
        r"(?:mi|ver|mostrar|cual es mi|que tengo en mi|revisar)\s*(?:inventario|mochila|equipo|objetos)",
        r"que\s*(?:llevo|tengo|cargo)",
        r"inventario",
    ]
    
    # Patrones para usar objetos
    USE_PATTERNS = [
        r"(?:uso|utilizo|bebo|tomo|aplico|consumo)\s+(?:una?\s+)?(.+)",
        r"me\s+(?:tomo|bebo)\s+(?:una?\s+)?(.+)",
    ]
    
    # Patrones para equipar/agarrar
    EQUIP_PATTERNS = [
        r"(?:agarro|empuno|desenvain[oa]|equipo|saco|tomo)\s+(?:mi\s+)?(.+)",
        r"(?:me\s+)?(?:pongo|equipo)\s+(?:mi\s+|la\s+|el\s+)?(.+)",
    ]
    
    # Patrones para guardar
    STORE_PATTERNS = [
        r"(?:guardo|envain[oa]|dejo|suelto)\s+(?:mi\s+)?(.+)",
    ]
    
    def __init__(self, campaign_manager):
        self.campaign_manager = campaign_manager
    
    def detect_inventory_intent(self, text: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        Detecta si el texto es una accion de inventario.
        
        Returns:
            Tuple de (tipo_accion, objeto) o None si no es inventario.
            Tipos: "view", "use", "equip", "store"
        """
        text_lower = text.lower().strip()
        
        # Verificar consulta de inventario
        for pattern in self.INVENTORY_PATTERNS:
            if re.search(pattern, text_lower):
                return ("view", None)
        
        # Verificar uso de objeto
        for pattern in self.USE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                item = match.group(1).strip()
                return ("use", item)
        
        # Verificar equipar
        for pattern in self.EQUIP_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                item = match.group(1).strip()
                return ("equip", item)
        
        # Verificar guardar
        for pattern in self.STORE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                item = match.group(1).strip()
                return ("store", item)
        
        return None
    
    def process_inventory_action(
        self, 
        player_id: int, 
        action_type: str, 
        item: str = None
    ) -> Dict[str, Any]:
        """
        Procesa una accion de inventario.
        
        Returns:
            Dict con "success", "message", "narrative" (opcional)
        """
        player = self.campaign_manager.get_player_by_telegram_id(player_id)
        if not player:
            return {
                "success": False,
                "message": "No tienes un personaje creado."
            }
        
        player_name = player.get("name", "Aventurero")
        
        if action_type == "view":
            return self._view_inventory(player, player_name)
        elif action_type == "use":
            return self._use_item(player, player_id, player_name, item)
        elif action_type == "equip":
            return self._equip_item(player, player_id, player_name, item)
        elif action_type == "store":
            return self._store_item(player, player_id, player_name, item)
        
        return {"success": False, "message": "Accion no reconocida."}
    
    def _view_inventory(self, player: Dict, player_name: str) -> Dict[str, Any]:
        """Muestra el inventario del jugador."""
        return {
            "success": True,
            "message": format_inventory_display(player),
            "is_display": True,  # Indica que es solo mostrar, no narrativa
        }
    
    def _use_item(
        self, 
        player: Dict, 
        player_id: int, 
        player_name: str, 
        item: str
    ) -> Dict[str, Any]:
        """Usa un objeto del inventario."""
        inventory = player.get("inventory", [])
        
        # Buscar el item (fuzzy match)
        found_item = self._find_item_in_list(item, inventory)
        
        if not found_item:
            return {
                "success": False,
                "message": f"No tienes '{item}' en tu inventario.",
            }
        
        # Verificar si es consumible
        is_potion = "pocion" in found_item.lower() or "potion" in found_item.lower()
        is_consumable = is_potion or "racion" in found_item.lower()
        
        if is_consumable:
            # Remover del inventario
            inventory.remove(found_item)
            self.campaign_manager.update_player_field(player_id, "inventory", inventory)
            
            if is_potion:
                return {
                    "success": True,
                    "message": f"Usaste: {found_item}",
                    "narrative": f"{player_name} bebe la {found_item}. El liquido baja por su garganta y siente como su cuerpo responde al efecto magico.",
                    "item_used": found_item,
                    "effect": "healing" if "curacion" in found_item.lower() or "healing" in found_item.lower() else "unknown"
                }
            else:
                return {
                    "success": True,
                    "message": f"Usaste: {found_item}",
                    "narrative": f"{player_name} usa {found_item}.",
                }
        else:
            # Item no consumible - solo narrativa
            return {
                "success": True,
                "message": f"Usas {found_item}",
                "narrative": f"{player_name} utiliza {found_item}.",
                "send_to_gameapi": True,  # Enviar a GameAPI para narrativa completa
            }
    
    def _equip_item(
        self, 
        player: Dict, 
        player_id: int, 
        player_name: str, 
        item: str
    ) -> Dict[str, Any]:
        """Equipa un arma u objeto."""
        equipment = player.get("equipment", {})
        inventory = player.get("inventory", [])
        weapons = equipment.get("weapons", [])
        
        # Buscar en armas equipadas
        found_weapon = self._find_item_in_list(item, weapons)
        
        if found_weapon:
            return {
                "success": True,
                "message": f"Empunas tu {found_weapon}",
                "narrative": f"{player_name} empuna su {found_weapon} con determinacion, listo para la accion.",
            }
        
        # Buscar en inventario
        found_item = self._find_item_in_list(item, inventory)
        
        if found_item:
            return {
                "success": True,
                "message": f"Sacas {found_item} de tu mochila",
                "narrative": f"{player_name} saca {found_item} de su mochila.",
            }
        
        # Verificar armadura
        armor = equipment.get("armor")
        if armor and item.lower() in armor.lower():
            return {
                "success": True,
                "message": f"Ya llevas puesta tu {armor}",
                "narrative": f"{player_name} ajusta su {armor}, asegurandose de que este bien colocada.",
            }
        
        return {
            "success": False,
            "message": f"No tienes '{item}' para equipar.",
        }
    
    def _store_item(
        self, 
        player: Dict, 
        player_id: int, 
        player_name: str, 
        item: str
    ) -> Dict[str, Any]:
        """Guarda un objeto."""
        equipment = player.get("equipment", {})
        weapons = equipment.get("weapons", [])
        
        found_weapon = self._find_item_in_list(item, weapons)
        
        if found_weapon:
            return {
                "success": True,
                "message": f"Guardas tu {found_weapon}",
                "narrative": f"{player_name} envaina su {found_weapon} cuidadosamente.",
            }
        
        return {
            "success": True,
            "message": f"Guardas {item}",
            "narrative": f"{player_name} guarda {item} en su mochila.",
        }
    
    def _find_item_in_list(self, search: str, items: list) -> Optional[str]:
        """Busca un item en una lista con fuzzy matching."""
        search_lower = search.lower().strip()
        
        # Busqueda exacta primero
        for item in items:
            if item.lower() == search_lower:
                return item
        
        # Busqueda parcial
        for item in items:
            if search_lower in item.lower() or item.lower() in search_lower:
                return item
        
        return None
    
    def add_item_to_inventory(self, player_id: int, item: str) -> bool:
        """Agrega un item al inventario del jugador."""
        player = self.campaign_manager.get_player_by_telegram_id(player_id)
        if not player:
            return False
        
        inventory = player.get("inventory", [])
        inventory.append(item)
        self.campaign_manager.update_player_field(player_id, "inventory", inventory)
        return True
    
    def remove_item_from_inventory(self, player_id: int, item: str) -> bool:
        """Remueve un item del inventario del jugador."""
        player = self.campaign_manager.get_player_by_telegram_id(player_id)
        if not player:
            return False
        
        inventory = player.get("inventory", [])
        found = self._find_item_in_list(item, inventory)
        
        if found:
            inventory.remove(found)
            self.campaign_manager.update_player_field(player_id, "inventory", inventory)
            return True
        
        return False
