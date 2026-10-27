(fn DropBag (Npc)
  (bind _b (Gioco|Generaattoredallaclasse :Class "/Game/Cousland/Areas/BP_Container.BP_Container_C" :SpawnTransform (Matematica|Trasforma|MakeTransform (Trasformazione|GetActorLocation Npc))))
  (Classe|BPContainer|Setup _b :InLook 5 :InName (Utilità|Stringa|Append (Classe|BPDlgNPC|OttieniDisplayName Npc) " (remains)") :bLocked "false" :InLevel 0.0 :InKey "" :bKeyReq "false" :bUsable "true")
  (Classe|BPContainer|SetLoot _b :InItems (Variabili|Predefinito|OttieniGItems) :InCounts (Variabili|Predefinito|OttieniGCounts) :InMoney (Variabili|Predefinito|OttieniGMoney)))
