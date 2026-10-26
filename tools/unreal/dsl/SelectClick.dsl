(fn SelectClick ()
  (bind (_hit _found) (Partita|Giocatore|GetHitResultUnderCursorbyChannel (Gioco|GetPlayerController 0) :TraceChannel "Visibility" :bTraceComplex "false"))
  (bind (_blocking _initial _time _distance _location _impact _normal _impactnormal _physmat _actor _component _hitbone _bone _item _element _face _start _end) (Collisione|BreakHitResult _hit))
  (Utilità|ControlloDiFlusso|Ramo _found
    (:then
      (Variabili|Predefinito|ImpostaPickNpc)
      (Funzionedichiamata|PickNpcNear :Where _location)
      (Funzionedichiamata|PickClicked :What _actor)
      (Funzionedichiamata|SelectRoute :What _actor))))
