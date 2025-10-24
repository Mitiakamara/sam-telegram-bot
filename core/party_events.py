# core/party_events.py
import random

class PartyEventSystem:
    """Sistema que gestiona las reacciones de S.A.M. ante eventos del grupo."""

    def __init__(self, narrator):
        self.narrator = narrator

    def on_player_join(self, party_size, player_name):
        if party_size == 1:
            msg = f"🌟 {player_name} ha llegado. La aventura comienza..."
        elif party_size <= 3:
            options = [
                f"🛡️ Un nuevo héroe se une a la causa: {player_name}.",
                f"🔥 {player_name} aparece en el horizonte, listo para el peligro.",
                f"✨ {player_name} se suma a la expedición. ¡Más fuerza para el grupo!"
            ]
            msg = random.choice(options)
        elif party_size == 4:
            msg = f"⚔️ {player_name} completa casi la compañía. ¡Solo falta un bardo o alguien que lleve las pociones!"
        elif party_size == 5:
            msg = f"🎉 {player_name} se une. ¡El grupo está completo! Que los dioses tiren los dados a su favor."
        else:
            msg = f"👥 {player_name} se une a esta multitud heroica. Esperemos que no haya que dividir el botín."
        self.narrator.speak(msg)

    def on_player_leave(self, party_size, player_name, kicked=False):
        if kicked:
            options = [
                f"💨 {player_name} fue lanzado por la ventana del gremio. ¡Ups!",
                f"🦶 {player_name} aprendió por las malas que las votaciones en este grupo son… letales.",
                f"⚡ {player_name} ha sido exiliado. ¡Que encuentre fortuna en otro lado!",
                f"🎲 {player_name} fue ‘teletransportado’… sin coordenadas seguras."
            ]
        else:
            options = [
                f"😔 {player_name} deja la compañía. El eco de sus pasos se pierde en la distancia.",
                f"🌙 {player_name} abandona el grupo, quizás para fundar su propia taberna.",
                f"🕯️ {player_name} se despide. Esperemos que pagara su parte de las pociones.",
                f"🏕️ {player_name} se marcha. El grupo se siente un poco más vacío... y más tranquilo."
            ]
        msg = random.choice(options)

        # Frases de ajuste según tamaño
        if party_size == 0:
            msg += " 🕯️ La fogata se apaga... La aventura se detiene, por ahora."
        elif party_size == 1:
            msg += " 🔹 Solo queda un valiente en pie."
        elif party_size == 2:
            msg += " 🧭 Un dúo formidable sobrevive. Que no falte el trabajo en equipo."

        self.narrator.speak(msg)
