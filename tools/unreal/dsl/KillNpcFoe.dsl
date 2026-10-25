(fn KillNpcFoe ()
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
  (Funzionedichiamata|TakeHit _npc :Damage 100000.0))
