"""Лабораторная работа № 7. Вариант 19. Ситникова Ольга, группа БИ2-1."""
import platform  # сведения о компьютере
import sys  # sys.getsizeof для размера таблиц
import time  # замер времени
import tracemalloc  # пик расхода памяти
from collections import Counter  # подсчёт монет каждого номинала
from itertools import product  # перебор для проверки ДП
import matplotlib.pyplot as plt  # графики

SUM, COINS = 300, [1, 7, 11]  # задача Б: сумма и номиналы по варианту 19
calls = 0  # счётчик вызовов рекурсивных функций


def p_naive(n, k):  # число разбиений n на слагаемые не больше k: наивная рекурсия
    global calls  # используем глобальный счётчик
    calls += 1  # считаем вызов
    if n == 0:  # нечего разбивать: одно (пустое) разбиение
        return 1  # базовый случай
    if k == 0:  # слагаемых не осталось, а n > 0
        return 0  # разбиений нет
    res = p_naive(n, k - 1)  # разбиения без слагаемого k
    if n >= k:  # слагаемое k можно использовать
        res += p_naive(n - k, k)  # разбиения, где k есть хотя бы один раз
    return res  # сумма двух случаев


def p_memo(n, k, cache):  # то же с мемоизацией (нисходящее ДП)
    global calls  # используем глобальный счётчик
    calls += 1  # считаем вызов
    if n == 0:  # базовый случай
        return 1  # одно разбиение
    if k == 0:  # слагаемых не осталось
        return 0  # разбиений нет
    if (n, k) not in cache:  # подзадача ещё не решена
        cache[n, k] = p_memo(n, k - 1, cache) + (p_memo(n - k, k, cache) if n >= k else 0)  # решаем и запоминаем
    return cache[n, k]  # берём результат из кэша


def p_iter(n):  # итеративное решение (восходящее ДП): Θ(n²) операций, O(n) памяти
    ways = [1] + [0] * n  # ways[s] — число разбиений s на уже рассмотренные слагаемые
    for k in range(1, n + 1):  # по очереди разрешаем слагаемое k
        for s in range(k, n + 1):  # обновляем все суммы, куда k помещается
            ways[s] += ways[s - k]  # добавляем разбиения суммы s - k со слагаемым k
    return ways[n]  # ответ для n


def timed(func, repeats):  # результат, лучшее время из повторов (с) и число вызовов функции func
    global calls  # используем глобальный счётчик
    times = []  # времена повторов
    for _ in range(repeats):  # несколько повторов
        calls = 0  # обнуляем счётчик вызовов
        t0 = time.perf_counter()  # начало замера
        res = func()  # запуск
        times.append(time.perf_counter() - t0)  # длительность повтора
    return res, min(times), calls  # результат, лучшее время (наименее искажённое помехами), вызовы


def coins_dp(total, coins, with_choice=False):  # размен: D[s] — минимум монет для суммы s
    D = [total + 1] * (total + 1)  # «бесконечность»: ответ не больше total, так как есть монета 1
    D[0] = 0  # для суммы 0 нужно 0 монет
    choice = [0] * (total + 1) if with_choice else None  # таблица выбора: какая монета дала минимум
    for s in range(1, total + 1):  # суммы по возрастанию
        for c in coins:  # перебираем номиналы
            if c <= s and D[s - c] + 1 < D[s]:  # монета подходит и улучшает результат
                D[s] = D[s - c] + 1  # D[s] = 1 + min D[s - c]
                if with_choice:  # нужна таблица выбора
                    choice[s] = c  # запоминаем монету
    return D, choice  # таблица значений и (при необходимости) таблица выбора


def restore_backtrack(D, total, coins):  # восстановление 1: обратный проход по таблице D
    res, s = [], total  # набранные монеты и остаток суммы
    while s > 0:  # пока сумма не разобрана
        c = next(c for c in coins if c <= s and D[s - c] == D[s] - 1)  # монета, ведущая к оптимуму
        res.append(c)  # добавляем монету
        s -= c  # уменьшаем остаток
    return res  # список монет


def restore_choice(choice, total):  # восстановление 2: по таблице выбора
    res, s = [], total  # набранные монеты и остаток суммы
    while s > 0:  # пока сумма не разобрана
        res.append(choice[s])  # берём сохранённую монету
        s -= choice[s]  # уменьшаем остаток
    return res  # список монет


def coins_brute(total, coins):  # полный перебор для проверки ДП (малые суммы)
    best = None  # лучшее найденное число монет
    for cnt in product(*(range(total // c + 1) for c in coins)):  # все наборы количеств монет
        if sum(n * c for n, c in zip(cnt, coins)) == total and (best is None or sum(cnt) < best):  # набор даёт сумму и лучше
            best = sum(cnt)  # запоминаем число монет
    return best  # минимальное число монет


def peak(func):  # пиковый расход памяти при выполнении func, байт
    tracemalloc.start()  # включаем отслеживание
    func()  # запуск
    top = tracemalloc.get_traced_memory()[1]  # пик
    tracemalloc.stop()  # выключаем отслеживание
    return top  # байт


if __name__ == "__main__":  # запуск только при прямом старте файла
    print(platform.platform(), "|", platform.processor() or platform.machine(), "| Python", platform.python_version())  # система
    print("\nЗадача А: число разбиений числа n")  # заголовок части А
    print("  n | наивная, с | вызовов | мемо, с | вызовов | итер., с | p(n) | вызовов/p(n)")  # заголовок таблицы
    rows = []  # строки результатов для графиков
    for n in [10, 20, 30, 35, 38, 50, 60, 65, 70, 75, 80]:  # значения из варианта (до 38) и далее для поиска предела
        r1, t1, c1 = timed(lambda: p_naive(n, n), 3 if n <= 38 else 1)  # наивная рекурсия
        r2, t2, c2 = timed(lambda: p_memo(n, n, {}), 21)  # мемоизация
        r3, t3, _ = timed(lambda: p_iter(n), 21)  # итеративная версия
        assert r1 == r2 == r3  # все три способа дают один ответ
        rows.append((n, t1, c1, t2, c2, t3))  # сохраняем строку
        print(f"{n:>3} | {t1:>10.4f} | {c1:>9} | {t2:>7.5f} | {c2:>7} | {t3:>8.6f} | {r1:>9} | {c1 / r1:>5.1f}")  # печать строки
        if t1 > 10:  # наивная версия вышла за ориентир 10 с
            print(f"Наивная рекурсия не укладывается в 10 с при n = {n}")  # предел найден
            break  # дальше не продолжаем
    print("\nЗадача Б: размен суммы", SUM, "номиналами", COINS)  # заголовок части Б
    for s in range(41):  # сверка ДП с полным перебором на малых суммах
        assert coins_dp(s, COINS)[0][s] == coins_brute(s, COINS)  # результаты должны совпасть
    print("Сверка ДП с полным перебором для S = 0..40: совпадение")  # итог сверки
    D, choice = coins_dp(SUM, COINS, True)  # решаем задачу с сохранением выбора
    print("Фрагмент таблицы D[0..22]:", D[:23])  # начало таблицы значений
    sol1, sol2 = restore_backtrack(D, SUM, COINS), restore_choice(choice, SUM)  # два способа восстановления
    assert sol1 == sol2 and sum(sol1) == SUM and len(sol1) == D[SUM]  # решения совпадают и корректны
    print(f"Минимум монет: {D[SUM]}; состав: {dict(sorted(Counter(sol1).items(), reverse=True))}")  # ответ с расшифровкой
    print("\nПамять восстановления (Г5), байт: пик tracemalloc и размер таблиц")  # заголовок сравнения
    for total in (SUM, 100_000):  # заданная сумма и большая сумма для наглядности
        m1 = peak(lambda: restore_backtrack(coins_dp(total, COINS)[0], total, COINS))  # способ 1: одна таблица
        m2 = peak(lambda: restore_choice(coins_dp(total, COINS, True)[1], total))  # способ 2: две таблицы
        Dt, Ct = coins_dp(total, COINS, True)  # таблицы для оценки размера списков
        print(f"  S = {total}: обратный проход {m1}, таблица выбора {m2}, список D {sys.getsizeof(Dt)}, список choice {sys.getsizeof(Ct)}")  # вывод
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))  # два графика рядом
    ns = [r[0] for r in rows]  # значения n
    ax1.plot(ns, [r[2] for r in rows], "o-", label="Наивная рекурсия")  # вызовы наивной версии
    ax1.plot(ns, [r[4] for r in rows], "o-", label="Мемоизация")  # вызовы мемоизации
    ax1.set(xlabel="n", ylabel="Число вызовов", title="Число вызовов", yscale="log")  # оформление
    ax2.plot(ns, [r[1] for r in rows], "o-", label="Наивная рекурсия")  # время наивной версии
    ax2.plot(ns, [r[3] for r in rows], "o-", label="Мемоизация")  # время мемоизации
    ax2.plot(ns, [r[5] for r in rows], "o-", label="Итеративная")  # время итеративной версии
    ax2.set(xlabel="n", ylabel="Время, с", title="Время работы", yscale="log")  # оформление
    for ax in (ax1, ax2):  # общее оформление
        ax.grid(True, alpha=0.3)  # сетка
        ax.legend()  # легенда
    plt.tight_layout()  # убираем наложение подписей
    plt.savefig("lab7_graphs.png", dpi=150)  # сохраняем график для отчёта
    plt.show()  # показываем график на экране
