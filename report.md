# Expansão em autoestados usada na animação

## 1. Modelo e discretização espacial

A animação representa a evolução temporal de um pacote de onda em um oscilador
harmônico unidimensional. No código, são usadas unidades com massa $m=1$ e
$\hbar=1$. O potencial é

$$
V(x)=\frac{1}{2}kx^2,
$$

e a frequência angular correspondente é $\omega=\sqrt{k}$. Essas relações
aparecem no código como `k`, `0.5*k*x**2` e `omega = np.sqrt(k)`.

O intervalo espacial é dividido em `n = 100` pontos:

$$
x_i \in [-1/2,1/2], \qquad
a = x_{i+1}-x_i,
$$

em que `x` contém as posições e `a` é o espaçamento uniforme da grade. A
segunda derivada é aproximada por diferenças finitas centrais:

$$
\left.\frac{d^2\psi}{dx^2}\right|_{x_i}
\approx \frac{\psi_{i-1}-2\psi_i+\psi_{i+1}}{a^2}.
$$

No código, `d2` é a matriz dessa aproximação. O Hamiltoniano discretizado é

$$
H=-\frac{1}{2}\frac{d^2}{dx^2}+V(x),
$$

implementado por `h = -0.5*d2 + np.diag(0.5*k*x**2)`. A chamada
`np.linalg.eigh(h)` diagonaliza essa matriz hermitiana:

$$
H v_n = E_n v_n.
$$

Os valores próprios $E_n$ são guardados em `eigenvalues`, e os vetores
próprios $v_n$, organizados como colunas, em `eigenvectors`. Assim,
`eigenvectors[:, n]` representa o vetor da $n$-ésima autofunção na grade.
`eigh` normaliza esses vetores com a norma euclidiana,
$\sum_i |v_n[i]|^2=1$, que não é a mesma normalização da integral contínua.

## 2. Estado inicial

O pacote inicial é uma gaussiana deslocada do centro do potencial:

$$
\psi(x,0) \propto
\exp\left[-\frac{(x-x_0)^2}{4\sigma^2}+i p_0x\right],
\qquad
\sigma=\frac{1}{\sqrt{2\omega}}.
$$

As variáveis correspondentes são:

| Expressão | Variável no código | Significado |
|---|---|---|
| $x$ | `x` | Pontos da grade espacial |
| $x_0$ | `x0 = -0.2` | Centro inicial do pacote |
| $p_0$ | `p0 = 0.0` | Momento inicial |
| $\omega$ | `omega = np.sqrt(k)` | Frequência angular |
| $\sigma$ | `sigma = 1 / np.sqrt(2 * omega)` | Largura do pacote |
| $\hbar$ | `hbar = 1.0` | Constante de Planck reduzida |

A expressão é construída em `psi0`. Em seguida, o código normaliza o pacote
com uma soma de Riemann:

$$
a\sum_i |\psi(x_i,0)|^2=1.
$$

Isso corresponde à linha `psi0 /= np.sqrt(a * np.sum(np.abs(psi0) ** 2))`.
O fator `a` é necessário porque a soma discreta aproxima a integral
$\int |\psi(x,0)|^2\,dx$.

## 3. Projeção nos autoestados

As autofunções contínuas aproximadas são obtidas a partir das colunas
normalizadas de `eigenvectors`:

$$
\phi_n(x_i)\approx \frac{v_n[i]}{\sqrt{a}}.
$$

O estado inicial pode ser escrito como uma combinação dessas autofunções:

$$
\psi(x,0)=\sum_n c_n\phi_n(x),
\qquad
c_n=\int \phi_n^*(x)\psi(x,0)\,dx.
$$

Na grade, a integral vira uma soma de Riemann:

$$
c_n\approx a\sum_i \phi_n^*(x_i)\psi(x_i,0)
=\sqrt{a}\sum_i v_n^*[i]\psi(x_i,0).
$$

Essa projeção para todos os estados é realizada por:

```python
coeficientes = np.sqrt(a) * (eigenvectors.conj().T @ psi0)
```

Portanto, `coeficientes[n]` é $c_n$, a amplitude complexa do estado inicial
no $n$-ésimo autoestado. A transposta conjugada (`conj().T`) implementa o
produto interno complexo; aqui os vetores próprios são reais, mas a função de
onda pode ser complexa.

## 4. Evolução temporal e reconstrução

Como cada autoestado satisfaz $H\phi_n=E_n\phi_n$, sua evolução temporal
apenas adquire uma fase:

$$
\phi_n(x,t)=\phi_n(x)e^{-iE_nt/\hbar}.
$$

Assim, a função de onda completa em cada instante é

$$
\psi(x,t)=\sum_n c_n e^{-iE_nt/\hbar}\phi_n(x).
$$

No código, `periodo = 2*np.pi/omega` define o período clássico do oscilador e
`tempos` cria 61 instantes entre $0$ e dois períodos. Para cada instante, a
reconstrução é feita por:

```python
(eigenvectors @ (coeficientes * np.exp(-1j * eigenvalues * t / hbar)))
/ np.sqrt(a)
```

Correspondência dos termos:

| Expressão matemática | Variável/expressão no código |
|---|---|
| $c_n$ | `coeficientes` |
| $E_n$ | `eigenvalues` |
| $e^{-iE_nt/\hbar}$ | `np.exp(-1j * eigenvalues * t / hbar)` |
| Soma sobre $n$ | `eigenvectors @ (...)` |
| Conversão de $v_n$ para $\phi_n$ | divisão por `np.sqrt(a)` |
| Conjunto de instantes $t$ | `tempos` |
| $\psi(x_i,t)$ para todos os instantes | `funcoes_onda` |

A divisão final por $\sqrt{a}$ converte a normalização discreta dos vetores
próprios para a escala de função de onda contínua. A densidade de probabilidade
é então calculada como

$$
\rho(x,t)=|\psi(x,t)|^2,
$$

correspondendo a `densidades = np.abs(funcoes_onda) ** 2`. É essa densidade que
a linha azul da animação apresenta; a linha tracejada cinza é a densidade no
instante inicial.

## 5. Atualização da animação e posição média

A função `atualizar(frame)` escolhe a densidade `densidades[frame]` e substitui
os valores verticais da curva azul. Também calcula a posição média:

$$
\langle x\rangle(t)=\int x|\psi(x,t)|^2\,dx
\approx a\sum_i x_i|\psi(x_i,t)|^2.
$$

No código, isso é `a * np.sum(x * densidades[frame])`. O título da figura
mostra o instante `tempos[frame]` e essa posição média.

**Observação sobre a quantidade de quadros:** embora `tempos` tenha 61 valores,
a animação é criada com `frames=range(fps)` e `fps = 30`. Portanto, são usados
somente os índices de 0 a 29, e não todos os 61 instantes. Como os instantes
foram distribuídos por dois períodos, esses 30 quadros percorrem apenas os
primeiros 29 intervalos da sequência temporal. Além disso, `interval=40`
corresponde a 25 quadros por segundo; nesse trecho, `fps` está sendo usado
como quantidade de quadros, não como taxa de reprodução. Para mostrar os dois
períodos completos, a sequência de quadros deve percorrer todos os índices de
`tempos`.
