(fn Flicker ()
  (bind _t (Utilità|Testo|GetGameTimeinSeconds))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniFlickerLights)) 1)
    (:LoopBody
      (bind _p (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniFlickerPhase) _index))
      (bind _n (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Matematica|Casuale|PerlinNoise1D (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica _t 2.7) _p)) 0.45) (Utility|Operatori|Moltiplica (Matematica|Casuale|PerlinNoise1D (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica _t 9.0) (Utility|Operatori|Moltiplica _p 1.7))) 0.18)))
      (Rendering|Componenti|Luce|SetIntensity (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniFlickerLights) _index) (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniFlickerBase) _index) (Utility|Operatori|Aggiungi _n 1.0))))))
