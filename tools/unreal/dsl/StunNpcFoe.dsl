(fn StunNpcFoe (Seconds bFall)
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
  (Utilità|ControlloDiFlusso|Ramo bFall
    (:then
      (Funzionedichiamata|KnockFor _npc :Seconds Seconds))
    (:else
      (Funzionedichiamata|Stun _npc :Seconds Seconds :PartySize 4))))
