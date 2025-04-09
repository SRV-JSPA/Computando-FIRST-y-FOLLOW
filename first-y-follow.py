class Gramatica:
    def __init__(self):
        self.producciones = {}     
        self.terminales = set()   
        self.no_terminales = set() 
        self.simbolo_inicial = None 
        self.epsilon = 'ε'       
        self.fin_entrada = '$'    
        self.debug = False      

    def agregar_produccion(self, no_terminal, produccion):

        self.no_terminales.add(no_terminal)
        
        if no_terminal not in self.producciones:
            self.producciones[no_terminal] = []
            
        self.producciones[no_terminal].append(produccion)
        
    
    def establecer_inicial(self, simbolo):
        self.simbolo_inicial = simbolo
        self.no_terminales.add(simbolo)

    def identificar_terminales_no_terminales(self):

        self.terminales = set()
        
        for nt in self.no_terminales:
            for produccion in self.producciones.get(nt, []):
                for simbolo in produccion:
                    if simbolo != self.epsilon and simbolo not in self.no_terminales:
                        self.terminales.add(simbolo)

    def log(self, mensaje):
        if self.debug:
            print(f"DEBUG: {mensaje}")

    def calcular_first(self):
        first = {}
        
        for terminal in self.terminales:
            first[terminal] = {terminal}
            self.log(f"FIRST({terminal}) = {{{terminal}}}")
        
        first[self.epsilon] = {self.epsilon}
        self.log(f"FIRST({self.epsilon}) = {{{self.epsilon}}}")
        
        for nt in self.no_terminales:
            first[nt] = set()
            self.log(f"FIRST({nt}) inicializado como conjunto vacío")
        
        iter_count = 0
        cambio = True
        while cambio:
            iter_count += 1
            self.log(f"Iteración {iter_count} para calcular FIRST")
            cambio = False
            
            for A in self.no_terminales:
                self.log(f"Procesando no terminal: {A}")
                for produccion in self.producciones.get(A, []):
                    self.log(f"  Producción: {A} → {' '.join(produccion)}")
                    
                    if len(produccion) == 1 and produccion[0] == self.epsilon:
                        if self.epsilon not in first[A]:
                            self.log(f"    Añadiendo {self.epsilon} a FIRST({A})")
                            first[A].add(self.epsilon)
                            cambio = True
                        continue
                    
                    k = 0
                    can_derive_epsilon = True
                    
                    while k < len(produccion) and can_derive_epsilon:
                        current_symbol = produccion[k]
                        self.log(f"    Procesando símbolo {k+1}: {current_symbol}")
                        
                        if current_symbol in first:
                            can_derive_epsilon = self.epsilon in first[current_symbol]
                        else:
                            self.log(f"    ADVERTENCIA: Símbolo {current_symbol} no encontrado en FIRST")
                            can_derive_epsilon = False
                            
                            if current_symbol not in self.no_terminales and current_symbol != self.epsilon:
                                first[current_symbol] = {current_symbol}
                                self.log(f"    Añadido {current_symbol} como terminal: FIRST({current_symbol}) = {{{current_symbol}}}")
                        
                        current_first = first.get(current_symbol, set())
                        for terminal in current_first:
                            if terminal != self.epsilon and terminal not in first[A]:
                                self.log(f"    Añadiendo {terminal} de FIRST({current_symbol}) a FIRST({A})")
                                first[A].add(terminal)
                                cambio = True
                        
                        if not can_derive_epsilon:
                            self.log(f"    {current_symbol} no puede derivar ε, deteniendo procesamiento de esta producción")
                            break
                        
                        self.log(f"    {current_symbol} puede derivar ε, continuando con el siguiente símbolo")
                        k += 1
                    
                    if can_derive_epsilon and k == len(produccion):
                        if self.epsilon not in first[A]:
                            self.log(f"    Todos los símbolos pueden derivar ε, añadiendo {self.epsilon} a FIRST({A})")
                            first[A].add(self.epsilon)
                            cambio = True
            
            if self.debug:
                self.log("Estado actual de FIRST:")
                for simbolo in sorted(first.keys()):
                    self.log(f"  FIRST({simbolo}) = {{{', '.join(sorted(first[simbolo]))}}}")
        
        self.log(f"FIRST calculado después de {iter_count} iteraciones")
        return first

    def calcular_first_cadena(self, cadena, first):

        if not cadena:
            return {self.epsilon}
        
        result = set()
        
        i = 0
        
        todos_derivan_epsilon = True
        
        while i < len(cadena) and todos_derivan_epsilon:
            simbolo_actual = cadena[i]
            
            first_simbolo = first.get(simbolo_actual, {simbolo_actual})
            
            for terminal in first_simbolo:
                if terminal != self.epsilon:
                    result.add(terminal)
            
            todos_derivan_epsilon = self.epsilon in first_simbolo
            i += 1
        
        if todos_derivan_epsilon:
            result.add(self.epsilon)
        
        return result

    def calcular_follow(self, first):

        follow = {nt: set() for nt in self.no_terminales}
        
        follow[self.simbolo_inicial].add(self.fin_entrada)
        self.log(f"Inicializado FOLLOW({self.simbolo_inicial}) = {{{self.fin_entrada}}}")
        
        iter_count = 0
        cambio = True
        while cambio:
            iter_count += 1
            self.log(f"Iteración {iter_count} para calcular FOLLOW")
            cambio = False
            
            for A in self.no_terminales:
                self.log(f"Procesando FOLLOW de no terminal: {A}")
                for B in self.no_terminales:
                    for i_prod, produccion in enumerate(self.producciones.get(B, [])):
                        self.log(f"  Considerando producción {i_prod+1} de {B}: {B} → {' '.join(produccion)}")
                        
                        for i, simbolo in enumerate(produccion):
                            if simbolo != A:
                                continue
                            
                            self.log(f"    Encontrada ocurrencia de {A} en posición {i+1}")
                            
                            if i < len(produccion) - 1:
                                beta = produccion[i+1:]
                                self.log(f"    Caso B → αAβ: β = {' '.join(beta)}")
                                
                                first_beta = self.calcular_first_cadena(beta, first)
                                self.log(f"    FIRST(β) = {{{', '.join(sorted(first_beta))}}}")
                                
                                for terminal in first_beta:
                                    if terminal != self.epsilon and terminal not in follow[A]:
                                        self.log(f"      Añadiendo {terminal} a FOLLOW({A})")
                                        follow[A].add(terminal)
                                        cambio = True
                                
                                if self.epsilon in first_beta:
                                    self.log(f"    ε ∈ FIRST(β), añadiendo FOLLOW({B}) a FOLLOW({A})")
                                    self.log(f"    FOLLOW({B}) = {{{', '.join(sorted(follow[B]))}}}")
                                    
                                    for terminal in follow[B]:
                                        if terminal not in follow[A]:
                                            self.log(f"      Añadiendo {terminal} a FOLLOW({A})")
                                            follow[A].add(terminal)
                                            cambio = True
                            
                            elif i == len(produccion) - 1:
                                self.log(f"    Caso B → αA: añadiendo FOLLOW({B}) a FOLLOW({A})")
                                self.log(f"    FOLLOW({B}) = {{{', '.join(sorted(follow[B]))}}}")
                                
                                for terminal in follow[B]:
                                    if terminal not in follow[A]:
                                        self.log(f"      Añadiendo {terminal} a FOLLOW({A})")
                                        follow[A].add(terminal)
                                        cambio = True
            
            if self.debug:
                self.log("Estado actual de FOLLOW:")
                for nt in sorted(self.no_terminales):
                    self.log(f"  FOLLOW({nt}) = {{{', '.join(sorted(follow[nt]))}}}")
        
        self.log(f"FOLLOW calculado después de {iter_count} iteraciones")
        return follow

    def mostrar_first_follow(self, first, follow):
        print("Conjuntos FIRST:")
        for simbolo in sorted(self.no_terminales):
            simbolos_ordenados = sorted(first[simbolo])
            print(f"FIRST({simbolo}) = {{{', '.join(simbolos_ordenados)}}}")
        
        print("\nConjuntos FOLLOW:")
        for nt in sorted(self.no_terminales):
            simbolos_ordenados = sorted(follow[nt])
            print(f"FOLLOW({nt}) = {{{', '.join(simbolos_ordenados)}}}")

    def crear_tabla_ll1(self, first, follow):
        tabla = {nt: {t: None for t in self.terminales.union({self.fin_entrada})} 
                 for nt in self.no_terminales}
        
        for A in self.no_terminales:
            for i, produccion in enumerate(self.producciones.get(A, [])):
                first_alpha = self.calcular_first_cadena(produccion, first)
                
                for a in first_alpha:
                    if a != self.epsilon:
                        if tabla[A][a] is not None:
                            print(f"Conflicto en tabla LL(1): M[{A},{a}] ya tiene {tabla[A][a]}")
                        tabla[A][a] = (A, produccion, i)
                
                if self.epsilon in first_alpha:
                    for b in follow[A]:
                        if tabla[A][b] is not None:
                            print(f"Conflicto en tabla LL(1): M[{A},{b}] ya tiene {tabla[A][b]}")
                        tabla[A][b] = (A, produccion, i)
        
        return tabla


def analizar_cadena(gramatica, cadena, debug=False):

    old_debug = gramatica.debug
    gramatica.debug = debug
    
    def log(mensaje):
        if debug:
            print(f"DEBUG: {mensaje}")
    
    log("Calculando conjuntos FIRST...")
    first = gramatica.calcular_first()
    
    log("Calculando conjuntos FOLLOW...")
    follow = gramatica.calcular_follow(first)
    
    log("Creando tabla LL(1)...")
    tabla = gramatica.crear_tabla_ll1(first, follow)
    
    log(f"Terminales: {sorted(gramatica.terminales)}")
    log(f"No terminales: {sorted(gramatica.no_terminales)}")
    
    if 'id' in cadena:
        log(f"'id' está en FIRST(F)? {'id' in first.get('F', set())}")
        log(f"'id' está en FIRST(T)? {'id' in first.get('T', set())}")
        log(f"'id' está en FIRST(E)? {'id' in first.get('E', set())}")
        
        if 'E' in gramatica.no_terminales and 'id' in gramatica.terminales:
            log(f"Entrada en tabla M[E,id]: {tabla.get('E', {}).get('id')}")
    
    entrada = list(cadena) + [gramatica.fin_entrada]
    pos_entrada = 0
    
    pila = [gramatica.fin_entrada, gramatica.simbolo_inicial]
    
    print(f"\nAnálisis de la cadena: {' '.join(cadena)}")
    print(f"{'PILA':<30} | {'ENTRADA':<20} | {'ACCIÓN'}")
    print("-" * 70)
    
    while pila:
        pila_str = ' '.join(pila)
        entrada_actual = ' '.join(entrada[pos_entrada:])
        
        X = pila[-1]
        a = entrada[pos_entrada]
        
        log(f"Tope de pila: {X}, Símbolo actual: {a}")
        print(f"{pila_str:<30} | {entrada_actual:<20} | ", end="")
        
        if X in gramatica.terminales or X == gramatica.fin_entrada:
            if X == a:  
                pila.pop()
                pos_entrada += 1
                print(f"Match: {X}")
            else: 
                print(f"Error: se esperaba {X}, se encontró {a}")
                gramatica.debug = old_debug
                return False
        
        elif X in gramatica.no_terminales:
            if a in tabla.get(X, {}):
                if tabla[X][a] is not None:
                    _, produccion, _ = tabla[X][a]
                    prod_str = ' '.join(produccion) if produccion != [gramatica.epsilon] else gramatica.epsilon
                    print(f"Usar {X} → {prod_str}")
                    
                    pila.pop()
                    
                    if produccion != [gramatica.epsilon]:
                        for simbolo in reversed(produccion):
                            pila.append(simbolo)
                else:
                    print(f"Error: entrada en tabla M[{X},{a}] es None")
                    gramatica.debug = old_debug
                    return False
            else:
                print(f"Error: no hay entrada en la tabla para M[{X},{a}]")
                log(f"FIRST({X}) = {sorted(first.get(X, set()))}")
                log(f"FOLLOW({X}) = {sorted(follow.get(X, set()))}")
                
                log(f"Entradas en tabla para {X}:")
                for terminal, entrada in tabla.get(X, {}).items():
                    if entrada:
                        _, prod, _ = entrada
                        prod_str = ' '.join(prod) if prod != [gramatica.epsilon] else gramatica.epsilon
                        log(f"  M[{X},{terminal}] = {X} → {prod_str}")
                
                gramatica.debug = old_debug
                return False
        else:
            print(f"Error: símbolo desconocido en la pila: {X}")
            gramatica.debug = old_debug
            return False

    if pos_entrada >= len(entrada) - 1: 
        print("\nAnálisis completado: cadena aceptada")
        gramatica.debug = old_debug
        return True
    else:
        print(f"\nError: fin de análisis pero queda entrada sin consumir: {' '.join(entrada[pos_entrada:])}")
        gramatica.debug = old_debug
        return False


def crear_gramatica():
    g = Gramatica()
    
    g.establecer_inicial('E')

    g.no_terminales.add('E')
    g.no_terminales.add('E\'')
    g.no_terminales.add('T')
    g.no_terminales.add('T\'')
    g.no_terminales.add('F')
    
    g.agregar_produccion('E', ['T', 'E\''])
    g.agregar_produccion('E\'', ['+', 'T', 'E\''])
    g.agregar_produccion('E\'', [g.epsilon])
    g.agregar_produccion('T', ['F', 'T\''])
    g.agregar_produccion('T\'', ['*', 'F', 'T\''])
    g.agregar_produccion('T\'', [g.epsilon])
    g.agregar_produccion('F', ['(', 'E', ')'])
    g.agregar_produccion('F', ['id'])
    
    g.identificar_terminales_no_terminales()
    
    return g

if __name__ == "__main__":
    gramatica = crear_gramatica()
    
    print("GRAMÁTICA DE EJEMPLO:")
    print(f"Terminales: {sorted(gramatica.terminales)}")
    print(f"No Terminales: {sorted(gramatica.no_terminales)}")
    
    print("\nProducciones:")
    for nt in sorted(gramatica.no_terminales):
        for produccion in gramatica.producciones[nt]:
            prod_str = ' '.join(produccion) if produccion != [gramatica.epsilon] else gramatica.epsilon
            print(f"{nt} → {prod_str}")
    
    first = gramatica.calcular_first()
    follow = gramatica.calcular_follow(first)
    
    gramatica.mostrar_first_follow(first, follow)
    
    tabla = gramatica.crear_tabla_ll1(first, follow)
    
    print("\nTabla LL(1):")
    for nt in sorted(gramatica.no_terminales):
        for t in sorted(gramatica.terminales.union({gramatica.fin_entrada})):
            if tabla[nt][t] is not None:
                _, prod, _ = tabla[nt][t]
                prod_str = ' '.join(prod) if prod != [gramatica.epsilon] else gramatica.epsilon
                print(f"M[{nt},{t}] = {nt} → {prod_str}")
    
    print("\n" + "="*50)
    resultado = analizar_cadena(gramatica, ['id', '+', 'id', '*', 'id'])
    
    if not resultado:
        print("\n\n" + "="*50)
        print("EJECUTANDO ANÁLISIS CON DEPURACIÓN")
        print("="*50)
        analizar_cadena(gramatica, ['id', '+', 'id', '*', 'id'], debug=True)
    
    print("\n" + "="*50)
    print("Análisis de otra cadena: (id+id)*id")
    analizar_cadena(gramatica, ['(', 'id', '+', 'id', ')', '*', 'id'])