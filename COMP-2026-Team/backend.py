# backend.py
import sys
import os

# Ajout du dossier courant au path pour l'import du module 'run'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports API & Modules internes
from run.api import check_syntax, run_text
from run.parser_text import parse_program_text
from run.ram_machine import step, is_halted, RAMState

class MoteurRAM:
    """
    Pont entre l'interface graphique et la logique d'exécution RAM.
    """
    
    @staticmethod
    def verifier_syntaxe(code):
        """Vérifie la syntaxe via l'API et retourne un message formaté."""
        result = check_syntax(code)
        if result.ok:
            return True, "Syntaxe Correcte."
        
        err = result.error
        return False, f"Erreur ligne {err.line} : {err.message}\nContexte : {err.text}"

    @staticmethod
    def executer_tout(code, input_val):
        """Exécute le programme complet et formate la sortie."""
        result = run_text(code, input_value=input_val)
        
        if result.status == "OK":
            return (f"--- Exécution Terminée ---\n"
                    f"Status : {result.status}\n"
                    f"Étapes : {result.steps}\n"
                    f"Sortie (R1) : {result.output}")
            
        elif result.status == "TIMEOUT":
            return (f"--- Arrêt Forcé (Boucle Infinie ?) ---\n"
                    f"Status : {result.status}\n"
                    f"Étapes : {result.steps}\n"
                    f"Dernier PC : {result.final_pc}")
            
        return f"Erreur critique : {result.status}\nDétail : {result.error}"

    @staticmethod
    def executer_pas_a_pas(code, registre_etat_dict):
        """
        Exécute une seule instruction.
        Conversion : État GUI (Dict) -> État Moteur (RAMState) -> État GUI (Dict).
        """
        # 1. Parsing temporaire (le moteur est sans état persistant)
        programme, err = parse_program_text(code)
        if err: return registre_etat_dict

        # 2. Reconstruction de l'état machine depuis le GUI
        pc_actuel = registre_etat_dict.get('PC', 1)
        regs_seulement = {}
        
        for k, v in registre_etat_dict.items():
            # Filtre et conversion des clés "R0" -> 0
            if isinstance(k, str) and k.startswith('R'):
                try:
                    regs_seulement[int(k[1:])] = int(v)
                except ValueError: pass

        state = RAMState(pc=pc_actuel, regs=regs_seulement)

        # 3. Vérification de fin de programme
        if is_halted(state, len(programme)):
            return registre_etat_dict

        # 4. Exécution du step (sécurisé)
        try:
            new_state = step(state, programme)
        except Exception:
            return registre_etat_dict

        # 5. Conversion retour vers le GUI
        nouveau_dict = {'PC': new_state.pc, 'Acc': 0}
        
        for k, v in new_state.regs.items():
            nouveau_dict[f"R{k}"] = v
            
        # Force l'affichage de R0/R1 même si nuls (le moteur les supprime par optimisation)
        nouveau_dict.setdefault('R0', 0)
        nouveau_dict.setdefault('R1', 0)

        return nouveau_dict