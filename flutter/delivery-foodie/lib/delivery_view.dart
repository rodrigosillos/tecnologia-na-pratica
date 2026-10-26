import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'catalog.dart';
import 'delivery_controller.dart';
import 'order.dart';
import 'ui_kit.dart';

class DeliveryView extends StatefulWidget {
  const DeliveryView({super.key, required this.controller});
  final DeliveryController controller;
  @override
  State<DeliveryView> createState() => _DeliveryViewState();
}

class _DeliveryViewState extends State<DeliveryView> {
  final homeScroll = ScrollController();
  final categoryScroll = ScrollController();
  DeliveryController get c => widget.controller;
  @override
  void initState() {
    super.initState();
    c.addListener(syncScroll);
  }

  @override
  void didUpdateWidget(DeliveryView old) {
    super.didUpdateWidget(old);
    if (old.controller != c) {
      old.controller.removeListener(syncScroll);
      c.addListener(syncScroll);
    }
  }

  void syncScroll() {
    if (!mounted || !c.demo) return;
    for (final pair in [
      (homeScroll, c.homeOffset),
      (categoryScroll, c.categoryOffset),
    ]) {
      if (pair.$1.hasClients) {
        final target = pair.$2.clamp(0.0, pair.$1.position.maxScrollExtent);
        if ((pair.$1.offset - target).abs() > .01) pair.$1.jumpTo(target);
      }
    }
  }

  void showDemoInfo() => showDialog<void>(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text('Demonstração local'),
      content: const Text(
        'Nenhuma conta externa é conectada. Use um e-mail de exemplo e uma senha fictícia para experimentar o app.',
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Entendi'),
        ),
      ],
    ),
  );
  Widget page(DeliveryStage stage) => switch (stage) {
    DeliveryStage.splash => SplashPage(c: c),
    DeliveryStage.login => LoginPage(c: c, onInfo: showDemoInfo),
    DeliveryStage.home => HomePage(
      c: c,
      homeScroll: homeScroll,
      categoryScroll: categoryScroll,
      onInfo: showDemoInfo,
    ),
    DeliveryStage.detail => ProductPage(c: c),
    DeliveryStage.cart => CartPage(c: c),
    DeliveryStage.checkout || DeliveryStage.processing => CheckoutPage(c: c),
    DeliveryStage.confirmation => ConfirmationPage(c: c),
  };
  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: c,
    builder: (context, _) {
      WidgetsBinding.instance.addPostFrameCallback((_) => syncScroll());
      final transition = smooth(c.elapsed / .28);
      final moving = transition < 1 && c.previous != c.stage;
      final light =
          c.stage == DeliveryStage.login || c.stage == DeliveryStage.home;
      return Material(
        color: paper,
        child: Stack(
          children: [
            if (moving) Positioned.fill(child: page(c.previous)),
            Positioned.fill(
              child: Opacity(
                opacity: moving ? transition : 1,
                child: Transform.translate(
                  offset: Offset(moving ? (1 - transition) * 24 : 0, 0),
                  child: page(c.stage),
                ),
              ),
            ),
            Positioned(
              left: 0,
              right: 0,
              top: 0,
              child: PhoneStatus(light: light),
            ),
            Positioned(
              left: 128,
              bottom: 9,
              child: Container(
                width: 134,
                height: 4,
                decoration: BoxDecoration(
                  color: ink,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
            if (c.demo)
              Positioned.fill(
                child: IgnorePointer(
                  child: CustomPaint(painter: DemoPointer(c.clock)),
                ),
              ),
          ],
        ),
      );
    },
  );
  @override
  void dispose() {
    c.removeListener(syncScroll);
    homeScroll.dispose();
    categoryScroll.dispose();
    super.dispose();
  }
}

class SplashPage extends StatelessWidget {
  const SplashPage({super.key, required this.c});
  final DeliveryController c;
  @override
  Widget build(BuildContext context) {
    final t = c.clock;
    final arrival = smooth(t / .65), exit = smooth((t - 1.2) / .5);
    return ColoredBox(
      color: paper,
      child: Stack(
        children: [
          Positioned(
            left: -320 + 366 * arrival + 430 * exit,
            top: 220,
            width: 300,
            height: 300,
            child: const Courier(size: 300),
          ),
          at(
            20,
            532,
            350,
            Opacity(
              opacity: smooth((t - .35) / .3) * (1 - exit),
              child: txt(
                'Foodie.',
                size: 44,
                color: brandDark,
                weight: FontWeight.w700,
                align: TextAlign.center,
              ),
            ),
          ),
          at(
            20,
            590,
            350,
            Opacity(
              opacity: smooth((t - .55) / .3) * (1 - exit),
              child: txt(
                'Sua fome. Nosso caminho.',
                size: 15,
                color: muted,
                align: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key, required this.c, required this.onInfo});
  final DeliveryController c;
  final VoidCallback onInfo;
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool reveal = false;
  DeliveryController get c => widget.c;
  @override
  Widget build(BuildContext context) {
    Widget field({
      required String hint,
      required TextEditingController controller,
      required IconData icon,
      required Key key,
      bool password = false,
    }) {
      final active =
          c.demo &&
          (password
              ? c.clock >= 3.4 && c.clock < 4.0
              : c.clock >= 2.1 && c.clock < 3.2);
      return TextField(
        key: key,
        controller: controller,
        readOnly: c.demo,
        obscureText: password && !reveal,
        enableInteractiveSelection: !c.demo,
        keyboardType: password
            ? TextInputType.visiblePassword
            : TextInputType.emailAddress,
        textInputAction: password ? TextInputAction.done : TextInputAction.next,
        onChanged: password ? null : c.validateEmail,
        onSubmitted: password ? (_) => c.login() : null,
        style: const TextStyle(
          fontFamily: 'VoltioSans',
          fontSize: 14,
          color: ink,
        ),
        cursorColor: brandPrimary,
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: const TextStyle(fontSize: 14, color: muted),
          filled: true,
          fillColor: const Color(0xFFF2F5ED),
          contentPadding: const EdgeInsets.symmetric(
            vertical: 13,
            horizontal: 14,
          ),
          prefixIcon: Icon(icon, color: active ? brandPrimary : muted, size: 19),
          suffixIcon: password
              ? GestureDetector(
                  onTap: () => setState(() => reveal = !reveal),
                  child: Icon(
                    reveal
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                    color: muted,
                    size: 19,
                  ),
                )
              : null,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(28),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(28),
            borderSide: BorderSide(color: active ? brandPrimary : lineColor),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(28),
            borderSide: const BorderSide(color: brandPrimary),
          ),
        ),
      );
    }

    return ColoredBox(
      color: paper,
      child: Stack(
        children: [
          at(
            0,
            0,
            390,
            Container(
              height: 300,
              decoration: const BoxDecoration(
                gradient: brandGradient,
                borderRadius: BorderRadius.vertical(
                  bottom: Radius.circular(32),
                ),
              ),
            ),
          ),
          at(
            26,
            102,
            152,
            txt(
              'Foodie.',
              size: 33,
              color: Colors.white,
              weight: FontWeight.w700,
            ),
          ),
          at(
            27,
            151,
            141,
            txt(
              'Sua fome.\nNosso caminho.',
              size: 14,
              color: const Color(0xFFE4F0D2),
              height: 1.4,
            ),
          ),
          Positioned(
            left: 157,
            top: 65,
            width: 224,
            height: 224,
            child: Transform.translate(
              offset: Offset(16 * (1 - smooth(c.elapsed / .3)), 0),
              child: const Courier(size: 224),
            ),
          ),
          at(
            24,
            329,
            342,
            txt('Boas-vindas!', size: 28, weight: FontWeight.w700),
          ),
          at(
            25,
            368,
            340,
            txt('Seu próximo favorito está aqui.', size: 13, color: muted),
          ),
          at(
            24,
            403,
            342,
            field(
              hint: 'Seu e-mail',
              controller: c.email,
              icon: Icons.mail_outline_rounded,
              key: const ValueKey('email-field'),
            ),
          ),
          at(
            24,
            470,
            342,
            field(
              hint: 'Senha',
              controller: c.password,
              icon: Icons.lock_outline_rounded,
              key: const ValueKey('password-field'),
              password: true,
            ),
          ),
          if (c.emailError != null)
            at(38, 453, 315, txt(c.emailError!, size: 10, color: brandPrimary)),
          at(
            24,
            538,
            193,
            GestureDetector(
              key: const ValueKey('remember'),
              onTap: c.toggleRemember,
              child: SizedBox(
                height: 28,
                child: Row(
                  children: [
                    Container(
                      width: 18,
                      height: 18,
                      decoration: BoxDecoration(
                        color: c.remember ? brandPrimary : Colors.white,
                        borderRadius: BorderRadius.circular(5),
                        border: Border.all(color: c.remember ? brandPrimary : lineColor),
                      ),
                      child: c.remember
                          ? const Icon(
                              Icons.check_rounded,
                              color: Colors.white,
                              size: 14,
                            )
                          : null,
                    ),
                    const SizedBox(width: 7),
                    txt('Manter conectado', size: 11, color: muted),
                  ],
                ),
              ),
            ),
          ),
          at(
            229,
            544,
            136,
            GestureDetector(
              onTap: widget.onInfo,
              child: txt(
                'Esqueci minha senha',
                size: 11,
                color: brandDark,
                align: TextAlign.right,
              ),
            ),
          ),
          at(
            24,
            584,
            342,
            ActionButton(
              key: const ValueKey('login'),
              label: 'Entrar',
              onTap: c.login,
              busy: c.loginBusy,
              clock: c.clock,
            ),
          ),
          if (c.loginError != null)
            at(
              24,
              641,
              342,
              txt(c.loginError!, size: 10, color: brandPrimary, align: TextAlign.center),
            ),
          at(
            24,
            658,
            342,
            txt(
              'Ou continue com',
              size: 11,
              color: muted,
              align: TextAlign.center,
            ),
          ),
          for (final (x, name, icon) in [
            (24.0, 'Google', Icons.g_mobiledata_rounded),
            (202.0, 'Apple', Icons.apple),
          ])
            at(
              x,
              684,
              164,
              GestureDetector(
                onTap: widget.onInfo,
                child: Container(
                  height: 44,
                  decoration: card(
                    color: const Color(0xFFF2F5ED),
                    radius: 22,
                    border: Colors.transparent,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(icon, color: ink, size: 23),
                      const SizedBox(width: 8),
                      txt(name, size: 13, weight: FontWeight.w700),
                    ],
                  ),
                ),
              ),
            ),
          at(
            24,
            752,
            342,
            GestureDetector(
              onTap: widget.onInfo,
              child: RichText(
                textAlign: TextAlign.center,
                text: const TextSpan(
                  style: TextStyle(
                    fontFamily: 'VoltioSans',
                    fontSize: 11,
                    color: muted,
                  ),
                  children: [
                    TextSpan(text: 'Primeira vez por aqui? '),
                    TextSpan(
                      text: 'Cadastre-se',
                      style: TextStyle(
                        color: brandDark,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          at(
            24,
            798,
            342,
            txt(
              'Tecnologia na Prática · demonstração',
              size: 10,
              color: muted,
              align: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({
    super.key,
    required this.c,
    required this.homeScroll,
    required this.categoryScroll,
    required this.onInfo,
  });
  final DeliveryController c;
  final ScrollController homeScroll, categoryScroll;
  final VoidCallback onInfo;
  void scrollTo(double offset) {
    if (homeScroll.hasClients)
      homeScroll.animateTo(
        offset.clamp(0, homeScroll.position.maxScrollExtent),
        duration: const Duration(milliseconds: 450),
        curve: Curves.easeOutCubic,
      );
  }

  @override
  Widget build(BuildContext context) {
    final list = c.shownProducts;
    final bodyHeight = math.max(1268.0, 606 + (list.length / 2).ceil() * 224.0);
    Widget section(String name, {VoidCallback? onTap}) => Row(
      children: [
        txt(name, size: 17, weight: FontWeight.w700),
        const Spacer(),
        GestureDetector(
          onTap: onTap ?? () => scrollTo(580),
          child: txt(
            'Ver tudo',
            size: 11,
            color: brandDark,
            weight: FontWeight.w500,
          ),
        ),
      ],
    );
    return ColoredBox(
      color: paper,
      child: Stack(
        children: [
          Positioned(
            left: 0,
            right: 0,
            top: 126,
            height: 646,
            child: SingleChildScrollView(
              key: const ValueKey('home-scroll'),
              controller: homeScroll,
              physics: const ClampingScrollPhysics(),
              child: SizedBox(
                height: bodyHeight,
                child: Stack(
                  children: [
                    at(
                      18,
                      12,
                      354,
                      GestureDetector(
                        onTap: () => c.openProduct(products.first),
                        child: Container(
                          height: 132,
                          decoration: BoxDecoration(
                            gradient: brandGradient,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Stack(
                            clipBehavior: Clip.hardEdge,
                            children: [
                              at(
                                17,
                                17,
                                180,
                                txt(
                                  'Seu pedido,\nlogo aí.',
                                  size: 25,
                                  color: Colors.white,
                                  weight: FontWeight.w700,
                                ),
                              ),
                              at(
                                18,
                                85,
                                183,
                                txt(
                                  'Feito na hora, para você.',
                                  size: 11,
                                  color: const Color(0xFFE4F0D2),
                                ),
                              ),
                              Positioned(
                                right: -3,
                                top: -8,
                                width: 153,
                                height: 153,
                                child: const Courier(size: 153),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    at(
                      18,
                      167,
                      354,
                      section('Categorias', onTap: () => c.chooseCategory(0)),
                    ),
                    Positioned(
                      left: 18,
                      right: 0,
                      top: 194,
                      height: 84,
                      child: SingleChildScrollView(
                        key: const ValueKey('category-scroll'),
                        controller: categoryScroll,
                        scrollDirection: Axis.horizontal,
                        physics: const ClampingScrollPhysics(),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            for (var i = 0; i < categories.length; i++)
                              Padding(
                                padding: const EdgeInsets.only(right: 9),
                                child: GestureDetector(
                                  key: ValueKey('category-$i'),
                                  onTap: () => c.chooseCategory(i),
                                  child: Container(
                                    width: 65,
                                    height: 81,
                                    decoration: BoxDecoration(
                                      color: c.selectedCategory == i
                                          ? brandSoft
                                          : Colors.white,
                                      borderRadius: BorderRadius.circular(17),
                                      border: Border.all(
                                        color: c.selectedCategory == i
                                            ? const Color(0xFFC7DFAF)
                                            : lineColor,
                                      ),
                                    ),
                                    child: Column(
                                      children: [
                                        const SizedBox(height: 3),
                                        FoodArt(categoryArt[i], size: 51),
                                        const SizedBox(height: 3),
                                        txt(
                                          categories[i],
                                          size: 10,
                                          color: c.selectedCategory == i
                                              ? brandDark
                                              : ink,
                                          weight: FontWeight.w500,
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
                    at(18, 294, 354, section('Peça de novo')),
                    at(
                      18,
                      324,
                      354,
                      Row(
                        children: [
                          Expanded(
                            child: GestureDetector(
                              onTap: () => c.openProduct(products.first),
                              child: Container(
                                height: 74,
                                padding: const EdgeInsets.all(8),
                                decoration: card(radius: 15),
                                child: Row(
                                  children: [
                                    const FoodArt(0, size: 57),
                                    const SizedBox(width: 5),
                                    Expanded(
                                      child: Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          txt(
                                            'Da casa',
                                            size: 12,
                                            weight: FontWeight.w700,
                                          ),
                                          const SizedBox(height: 6),
                                          txt(
                                            'R\$ 29,90',
                                            size: 11,
                                            color: muted,
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: GestureDetector(
                              onTap: () => c.openProduct(products[1]),
                              child: Container(
                                height: 74,
                                padding: const EdgeInsets.all(8),
                                decoration: card(radius: 15),
                                child: Row(
                                  children: [
                                    const FoodArt(1, size: 57),
                                    const SizedBox(width: 5),
                                    Expanded(
                                      child: Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          txt(
                                            'Pepperoni',
                                            size: 12,
                                            weight: FontWeight.w700,
                                          ),
                                          const SizedBox(height: 6),
                                          txt(
                                            'R\$ 24,90',
                                            size: 11,
                                            color: muted,
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    at(18, 420, 354, section('Para matar a fome')),
                    at(
                      18,
                      450,
                      354,
                      Row(
                        children: [
                          Expanded(
                            child: GestureDetector(
                              onTap: () => c.openProduct(products.first),
                              child: Container(
                                height: 100,
                                decoration: card(
                                  color: brandSoft,
                                  border: Colors.transparent,
                                  radius: 16,
                                ),
                                child: Stack(
                                  children: [
                                    at(
                                      12,
                                      13,
                                      142,
                                      txt(
                                        'Seu favorito\nde novo',
                                        size: 17,
                                        color: brandDark,
                                        weight: FontWeight.w700,
                                      ),
                                    ),
                                    at(
                                      12,
                                      75,
                                      106,
                                      Row(
                                        children: [
                                          txt(
                                            'Pedir agora',
                                            size: 10,
                                            color: brandDark,
                                          ),
                                          const SizedBox(width: 4),
                                          const Icon(
                                            Icons.arrow_forward_rounded,
                                            size: 11,
                                            color: brandDark,
                                          ),
                                        ],
                                      ),
                                    ),
                                    const Positioned(
                                      right: 0,
                                      bottom: 2,
                                      child: FoodArt(0, size: 68),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: GestureDetector(
                              onTap: () => c.openProduct(products[2]),
                              child: Container(
                                height: 100,
                                decoration: card(
                                  color: const Color(0xFFFFF1DF),
                                  border: Colors.transparent,
                                  radius: 16,
                                ),
                                child: Stack(
                                  children: [
                                    at(
                                      12,
                                      13,
                                      142,
                                      txt(
                                        'Crocante\naté o fim',
                                        size: 17,
                                        color: const Color(0xFF8B572B),
                                        weight: FontWeight.w700,
                                      ),
                                    ),
                                    at(
                                      12,
                                      75,
                                      104,
                                      txt(
                                        'A partir de R\$ 14,90',
                                        size: 9,
                                        color: const Color(0xFF8B572B),
                                      ),
                                    ),
                                    const Positioned(
                                      right: 0,
                                      bottom: 0,
                                      child: FoodArt(2, size: 63),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    at(
                      18,
                      575,
                      354,
                      section(
                        c.showSaved
                            ? 'Seus favoritos'
                            : c.selectedCategory == 0
                            ? 'Mais pedidos'
                            : categories[c.selectedCategory],
                      ),
                    ),
                    if (list.isEmpty)
                      at(
                        20,
                        650,
                        350,
                        txt(
                          'Seus favoritos aparecem aqui.\nToque no coração de um produto.',
                          size: 15,
                          color: muted,
                          align: TextAlign.center,
                        ),
                      ),
                    for (var i = 0; i < list.length; i++)
                      at(
                        18 + (i % 2) * 181,
                        606 + (i ~/ 2) * 224,
                        173,
                        ProductTile(product: list[i], c: c),
                      ),
                  ],
                ),
              ),
            ),
          ),
          at(
            0,
            0,
            390,
            Container(
              height: 126,
              decoration: const BoxDecoration(
                gradient: brandGradient,
                borderRadius: BorderRadius.vertical(
                  bottom: Radius.circular(25),
                ),
              ),
            ),
          ),
          at(
            20,
            64,
            39,
            Container(
              height: 39,
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.person_outline_rounded,
                color: brandDark,
                size: 26,
              ),
            ),
          ),
          at(
            70,
            64,
            240,
            txt('Entregar em', size: 10, color: const Color(0xFFE4F0D2)),
          ),
          at(
            70,
            81,
            250,
            Row(
              children: [
                txt(
                  'Casa',
                  size: 13,
                  color: Colors.white,
                  weight: FontWeight.w700,
                ),
                const SizedBox(width: 5),
                txt('Rua Exemplo, 123', size: 11, color: Colors.white),
                const Icon(
                  Icons.keyboard_arrow_down_rounded,
                  color: Colors.white,
                  size: 15,
                ),
              ],
            ),
          ),
          at(
            333,
            64,
            36,
            RoundButton(
              icon: Icons.notifications_none_rounded,
              onTap: onInfo,
              fill: brandDark,
              color: Colors.white,
              size: 36,
            ),
          ),
          at(
            0,
            772,
            390,
            Container(
              height: 58,
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: lineColor)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  nav(Icons.home_outlined, 'Início', 0, () => c.home()),
                  nav(Icons.favorite_border_rounded, 'Salvos', 1, () {
                    c.showFavorites();
                    scrollTo(580);
                  }),
                  nav(
                    Icons.shopping_bag_outlined,
                    'Carrinho',
                    2,
                    c.openCart,
                    count: c.cartCount,
                  ),
                  nav(
                    Icons.local_offer_outlined,
                    'Ofertas',
                    3,
                    () => scrollTo(400),
                  ),
                  nav(Icons.person_outline_rounded, 'Perfil', 4, onInfo),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget nav(
    IconData icon,
    String label,
    int index,
    VoidCallback onTap, {
    int count = 0,
  }) => GestureDetector(
    key: ValueKey('nav-$index'),
    onTap: onTap,
    behavior: HitTestBehavior.opaque,
    child: SizedBox(
      width: 65,
      height: 55,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Icon(icon, color: c.navTab == index ? brandPrimary : muted, size: 21),
              if (count > 0)
                Positioned(
                  right: -7,
                  top: -5,
                  child: Container(
                    width: 15,
                    height: 15,
                    alignment: Alignment.center,
                    decoration: const BoxDecoration(
                      color: brandPrimary,
                      shape: BoxShape.circle,
                    ),
                    child: txt('$count', size: 9, color: Colors.white),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 4),
          txt(label, size: 9, color: c.navTab == index ? brandPrimary : muted),
        ],
      ),
    ),
  );
}

class ProductTile extends StatelessWidget {
  const ProductTile({super.key, required this.product, required this.c});
  final Product product;
  final DeliveryController c;
  @override
  Widget build(BuildContext context) => GestureDetector(
    key: ValueKey('product-${product.id}'),
    onTap: () => c.openProduct(product),
    child: Container(
      height: 210,
      decoration: card(radius: 17),
      child: Stack(
        children: [
          at(
            8,
            13,
            157,
            txt(
              product.name,
              size: 12,
              weight: FontWeight.w700,
              align: TextAlign.center,
              maxLines: 1,
            ),
          ),
          at(
            8,
            34,
            157,
            txt(
              money(product.price),
              size: 12,
              color: muted,
              align: TextAlign.center,
            ),
          ),
          const SizedBox(),
          Positioned(left: 27, top: 55, child: FoodArt(product.art, size: 119)),
          at(
            12,
            179,
            105,
            Row(
              children: [
                const Icon(Icons.schedule_rounded, size: 12, color: muted),
                const SizedBox(width: 4),
                txt(
                  '${product.minutes}–${product.minutes + 10} min',
                  size: 10,
                  color: muted,
                ),
              ],
            ),
          ),
          at(
            136,
            170,
            26,
            GestureDetector(
              key: ValueKey('quick-add-${product.id}'),
              onTap: () => c.add(product),
              child: Container(
                height: 26,
                decoration: BoxDecoration(
                  color: brandSoft,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.add_rounded, color: brandPrimary, size: 18),
              ),
            ),
          ),
        ],
      ),
    ),
  );
}

class PageTop extends StatelessWidget {
  const PageTop({
    super.key,
    required this.title,
    required this.onBack,
    this.trailing,
  });
  final String title;
  final VoidCallback onBack;
  final Widget? trailing;
  @override
  Widget build(BuildContext context) => SizedBox(
    height: 112,
    child: Stack(
      children: [
        at(
          20,
          64,
          40,
          RoundButton(
            key: const ValueKey('back'),
            icon: Icons.arrow_back_rounded,
            onTap: onBack,
            fill: Colors.white,
          ),
        ),
        at(76, 70, 268, txt(title, size: 23, weight: FontWeight.w700)),
        if (trailing != null) Positioned(right: 21, top: 64, child: trailing!),
      ],
    ),
  );
}

class ProductPage extends StatelessWidget {
  const ProductPage({super.key, required this.c});
  final DeliveryController c;
  @override
  Widget build(BuildContext context) {
    final p = c.selected;
    return ColoredBox(
      color: paper,
      child: Stack(
        children: [
          at(
            0,
            0,
            390,
            Container(
              height: 370,
              decoration: const BoxDecoration(
                color: Color(0xFFF0F5E7),
                borderRadius: BorderRadius.vertical(
                  bottom: Radius.circular(35),
                ),
              ),
            ),
          ),
          at(
            20,
            64,
            40,
            RoundButton(icon: Icons.arrow_back_rounded, onTap: () => c.home()),
          ),
          at(
            278,
            64,
            40,
            RoundButton(
              key: const ValueKey('detail-cart'),
              icon: Icons.shopping_bag_outlined,
              onTap: c.openCart,
              count: c.cartCount,
            ),
          ),
          at(
            330,
            64,
            40,
            RoundButton(
              key: const ValueKey('favorite'),
              icon: c.favorites.contains(p.id)
                  ? Icons.favorite_rounded
                  : Icons.favorite_border_rounded,
              onTap: () => c.toggleFavorite(p),
              color: brandPrimary,
            ),
          ),
          Positioned(
            left: 77,
            top: 124,
            child: Transform.scale(
              scale: .95 + .05 * smooth(c.elapsed / .35),
              child: FoodArt(p.art, size: 236),
            ),
          ),
          at(24, 395, 342, txt(p.name, size: 26, weight: FontWeight.w700)),
          at(
            24,
            439,
            208,
            txt(
              money(p.price),
              size: 27,
              color: brandDark,
              weight: FontWeight.w700,
            ),
          ),
          at(
            276,
            443,
            90,
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Icon(
                  Icons.star_rounded,
                  color: Color(0xFFF3B341),
                  size: 19,
                ),
                const SizedBox(width: 3),
                txt('4,9', size: 14, weight: FontWeight.w700),
              ],
            ),
          ),
          at(
            24,
            490,
            342,
            txt(p.description, size: 14, color: muted, height: 1.45),
          ),
          at(24, 582, 342, Container(height: 1, color: lineColor)),
          at(
            24,
            605,
            342,
            Row(
              children: [
                const Icon(Icons.schedule_rounded, color: brandPrimary, size: 19),
                const SizedBox(width: 8),
                txt('${p.minutes}–${p.minutes + 10} min', size: 13),
                const Spacer(),
                const Icon(Icons.delivery_dining_rounded, color: brandPrimary, size: 20),
                const SizedBox(width: 7),
                txt('Entrega R\$ 4,90', size: 13),
              ],
            ),
          ),
          at(
            24,
            655,
            342,
            Container(
              height: 41,
              padding: const EdgeInsets.symmetric(horizontal: 13),
              decoration: card(color: Colors.white, radius: 12),
              child: Row(
                children: [
                  const Icon(Icons.restaurant_rounded, color: muted, size: 16),
                  const SizedBox(width: 8),
                  txt('Preparado na hora', size: 12, color: muted),
                ],
              ),
            ),
          ),
          at(
            24,
            730,
            342,
            ActionButton(
              key: const ValueKey('add-to-cart'),
              label: c.addFeedback > 0
                  ? 'Adicionado ao carrinho'
                  : 'Adicionar · ${money(p.price)}',
              onTap: () => c.add(p),
              icon: c.addFeedback > 0 ? Icons.check_rounded : Icons.add_rounded,
            ),
          ),
          at(
            24,
            800,
            342,
            txt(
              'Demonstração · sem pedido real',
              size: 10,
              color: muted,
              align: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
}

class CartPage extends StatelessWidget {
  const CartPage({super.key, required this.c});
  final DeliveryController c;
  @override
  Widget build(BuildContext context) {
    final items = products.where((p) => c.cart.containsKey(p.id)).toList();
    return ColoredBox(
      color: paper,
      child: Stack(
        children: [
          Positioned(
            left: 0,
            right: 0,
            top: 0,
            child: PageTop(title: 'Seu carrinho', onBack: () => c.home()),
          ),
          at(
            24,
            119,
            342,
            txt('Seu pedido chega quentinho.', size: 13, color: muted),
          ),
          if (items.isEmpty)
            at(
              25,
              260,
              340,
              Column(
                children: [
                  const Icon(Icons.shopping_bag_outlined, size: 64, color: brandPrimary),
                  const SizedBox(height: 22),
                  txt(
                    'Seu carrinho está vazio',
                    size: 22,
                    weight: FontWeight.w700,
                  ),
                  const SizedBox(height: 12),
                  txt(
                    'Escolha algo gostoso para começar.',
                    size: 14,
                    color: muted,
                  ),
                ],
              ),
            )
          else
            Positioned(
              left: 20,
              right: 20,
              top: 153,
              height: 366,
              child: SingleChildScrollView(
                key: const ValueKey('cart-scroll'),
                child: Column(
                  children: [
                    for (final p in items)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Container(
                          height: 139,
                          decoration: card(),
                          child: Stack(
                            children: [
                              Positioned(
                                left: 8,
                                top: 15,
                                child: FoodArt(p.art, size: 102),
                              ),
                              at(
                                121,
                                18,
                                207,
                                txt(
                                  p.name,
                                  size: 17,
                                  weight: FontWeight.w700,
                                  maxLines: 2,
                                ),
                              ),
                              at(
                                121,
                                64,
                                196,
                                txt(
                                  money(p.price),
                                  size: 16,
                                  color: brandDark,
                                  weight: FontWeight.w700,
                                ),
                              ),
                              at(
                                211,
                                81,
                                124,
                                Container(
                                  height: 38,
                                  decoration: card(radius: 11),
                                  child: Row(
                                    children: [
                                      GestureDetector(
                                        key: ValueKey('minus-${p.id}'),
                                        onTap: () => c.changeQuantity(p, -1),
                                        behavior: HitTestBehavior.opaque,
                                        child: const SizedBox(
                                          width: 39,
                                          height: 36,
                                          child: Icon(
                                            Icons.remove_rounded,
                                            color: muted,
                                            size: 19,
                                          ),
                                        ),
                                      ),
                                      Expanded(
                                        child: Center(
                                          child: txt(
                                            '${c.cart[p.id]}',
                                            size: 16,
                                            weight: FontWeight.w700,
                                          ),
                                        ),
                                      ),
                                      GestureDetector(
                                        key: ValueKey('plus-${p.id}'),
                                        onTap: () => c.changeQuantity(p, 1),
                                        behavior: HitTestBehavior.opaque,
                                        child: Container(
                                          width: 39,
                                          height: 36,
                                          decoration: BoxDecoration(
                                            color: brandSoft,
                                            borderRadius: BorderRadius.circular(
                                              10,
                                            ),
                                          ),
                                          child: const Icon(
                                            Icons.add_rounded,
                                            color: brandPrimary,
                                            size: 19,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    GestureDetector(
                      key: const ValueKey('add-more'),
                      onTap: () => c.home(),
                      child: Container(
                        height: 42,
                        alignment: Alignment.center,
                        decoration: card(
                          color: paper,
                          border: const Color(0xFFC7DFAF),
                          radius: 13,
                        ),
                        child: txt(
                          '+ Adicionar mais itens',
                          size: 13,
                          color: brandPrimary,
                          weight: FontWeight.w700,
                        ),
                      ),
                    ),
                    const SizedBox(height: 25),
                    Align(
                      alignment: Alignment.centerLeft,
                      child: txt(
                        'Combina com seu pedido',
                        size: 15,
                        weight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      height: 85,
                      padding: const EdgeInsets.all(8),
                      decoration: card(),
                      child: Row(
                        children: [
                          const FoodArt(2, size: 69),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                txt(
                                  'Batata crocante',
                                  size: 14,
                                  weight: FontWeight.w700,
                                ),
                                const SizedBox(height: 6),
                                txt('R\$ 14,90', size: 12, color: muted),
                              ],
                            ),
                          ),
                          RoundButton(
                            key: const ValueKey('add-fries'),
                            icon: Icons.add_rounded,
                            onTap: () => c.add(products[2]),
                            color: brandPrimary,
                            fill: brandSoft,
                            size: 31,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          at(20, 555, 350, TotalsCard(c: c)),
          at(
            24,
            742,
            342,
            ActionButton(
              key: const ValueKey('checkout'),
              label: 'Continuar pedido',
              onTap: c.checkout,
              enabled: c.cartCount > 0,
            ),
          ),
          at(
            24,
            804,
            342,
            txt(
              'Tudo pronto? Confira antes de continuar.',
              size: 10,
              color: muted,
              align: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
}

class TotalsCard extends StatelessWidget {
  const TotalsCard({super.key, required this.c});
  final DeliveryController c;
  @override
  Widget build(BuildContext context) => Container(
    height: 159,
    padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 18),
    decoration: card(),
    child: Column(
      children: [
        row('Subtotal', money(c.subtotal)),
        const SizedBox(height: 16),
        row('Taxa de entrega', money(c.deliveryFee)),
        const SizedBox(height: 17),
        Container(height: 1, color: lineColor),
        const SizedBox(height: 14),
        Row(
          children: [
            txt('Total', size: 20, weight: FontWeight.w700),
            const Spacer(),
            Transform.scale(
              scale: 1 + .045 * smooth((c.quantityFeedback / .35)),
              child: txt(
                money(c.total),
                size: 23,
                color: brandDark,
                weight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ],
    ),
  );
  Widget row(String a, String b) => Row(
    children: [
      txt(a, size: 13, color: muted),
      const Spacer(),
      txt(b, size: 14, weight: FontWeight.w500),
    ],
  );
}

class CheckoutPage extends StatelessWidget {
  const CheckoutPage({super.key, required this.c});
  final DeliveryController c;
  @override
  Widget build(BuildContext context) => ColoredBox(
    color: paper,
    child: Stack(
      children: [
        Positioned(
          left: 0,
          right: 0,
          top: 0,
          child: PageTop(
            title: 'Finalizar pedido',
            onBack: () {
              if (c.stage != DeliveryStage.processing) c.go(DeliveryStage.cart);
            },
          ),
        ),
        at(
          24,
          125,
          342,
          txt('Endereço de entrega', size: 16, weight: FontWeight.w700),
        ),
        at(
          20,
          153,
          350,
          Container(
            height: 92,
            padding: const EdgeInsets.all(15),
            decoration: card(),
            child: Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: brandSoft,
                    borderRadius: BorderRadius.circular(13),
                  ),
                  child: const Icon(
                    Icons.location_on_outlined,
                    color: brandPrimary,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      txt(
                        c.selectedAddress == 0 ? 'Casa' : 'Trabalho',
                        size: 15,
                        weight: FontWeight.w700,
                      ),
                      const SizedBox(height: 4),
                      txt(c.address, size: 12),
                      const SizedBox(height: 3),
                      txt('Endereço demonstrativo', size: 10, color: muted),
                    ],
                  ),
                ),
                GestureDetector(
                  key: const ValueKey('change-address'),
                  onTap: () {
                    if (c.stage != DeliveryStage.processing)
                      c.chooseAddress(1 - c.selectedAddress);
                  },
                  child: txt(
                    'Trocar',
                    size: 11,
                    color: brandPrimary,
                    weight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
        ),
        at(
          24,
          267,
          342,
          txt('Como prefere pagar?', size: 16, weight: FontWeight.w700),
        ),
        at(
          20,
          296,
          350,
          paymentTile(
            PaymentMethod.cardOnDelivery,
            'Cartão na entrega',
            'Pague ao receber',
            Icons.credit_card_rounded,
          ),
        ),
        at(
          20,
          379,
          350,
          paymentTile(
            PaymentMethod.cash,
            'Dinheiro',
            'Pagamento na entrega',
            Icons.payments_outlined,
          ),
        ),
        at(
          24,
          478,
          342,
          Row(
            children: [
              txt('Resumo do pedido', size: 16, weight: FontWeight.w700),
              const Spacer(),
              txt('${c.cartCount} itens', size: 12, color: muted),
            ],
          ),
        ),
        at(20, 512, 350, TotalsCard(c: c)),
        at(
          24,
          695,
          342,
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.info_outline_rounded, size: 14, color: muted),
              const SizedBox(width: 6),
              txt('Nenhuma cobrança neste app', size: 11, color: muted),
            ],
          ),
        ),
        at(
          24,
          742,
          342,
          ActionButton(
            key: const ValueKey('confirm-order'),
            label: 'Confirmar pedido',
            onTap: c.confirm,
            enabled: c.canConfirm || c.stage == DeliveryStage.processing,
            busy: c.stage == DeliveryStage.processing,
            clock: c.clock,
          ),
        ),
      ],
    ),
  );
  Widget paymentTile(
    PaymentMethod method,
    String title,
    String description,
    IconData icon,
  ) {
    final selected = c.payment == method;
    return GestureDetector(
      key: ValueKey(
        method == PaymentMethod.cardOnDelivery ? 'pay-card' : 'pay-cash',
      ),
      onTap: () {
        if (c.stage != DeliveryStage.processing) c.choosePayment(method);
      },
      child: Container(
        height: 70,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        decoration: card(
          color: selected ? brandSoft : Colors.white,
          border: selected ? brandPrimary : lineColor,
          radius: 16,
        ),
        child: Row(
          children: [
            Icon(icon, color: selected ? brandPrimary : muted, size: 25),
            const SizedBox(width: 15),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  txt(title, size: 15, weight: FontWeight.w700),
                  const SizedBox(height: 5),
                  txt(description, size: 12, color: muted),
                ],
              ),
            ),
            Container(
              width: 21,
              height: 21,
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: selected ? brandPrimary : const Color(0xFFC9D0C1),
                  width: 1.5,
                ),
              ),
              child: selected
                  ? Container(
                      decoration: const BoxDecoration(
                        color: brandPrimary,
                        shape: BoxShape.circle,
                      ),
                    )
                  : null,
            ),
          ],
        ),
      ),
    );
  }
}

class ConfirmationPage extends StatelessWidget {
  const ConfirmationPage({super.key, required this.c});
  final DeliveryController c;
  @override
  Widget build(BuildContext context) {
    final order = c.order;
    if (order == null) return const ColoredBox(color: paper);
    final progress = c.detailsProgress.clamp(0.0, 1.0);
    return ColoredBox(
      color: paper,
      child: Stack(
        children: [
          Positioned(
            left: 145,
            top: 103,
            width: 100,
            height: 100,
            child: Transform.scale(
              scale: .8 + .2 * smooth(c.elapsed / .35),
              child: Container(
                padding: const EdgeInsets.all(25),
                decoration: const BoxDecoration(
                  color: brandPrimary,
                  shape: BoxShape.circle,
                ),
                child: CustomPaint(
                  painter: CheckPainter(smooth((c.elapsed - .15) / .5)),
                ),
              ),
            ),
          ),
          at(
            18,
            220,
            354,
            txt(
              'Pedido confirmado!',
              size: 27,
              weight: FontWeight.w700,
              align: TextAlign.center,
            ),
          ),
          at(
            20,
            260,
            350,
            txt(
              'Já recebemos seu pedido.',
              size: 14,
              color: muted,
              align: TextAlign.center,
            ),
          ),
          at(
            125,
            291,
            140,
            Container(
              height: 28,
              alignment: Alignment.center,
              decoration: card(
                color: brandSoft,
                border: Colors.transparent,
                radius: 14,
              ),
              child: txt(
                'Pedido #${order.number}',
                size: 11,
                color: brandDark,
                weight: FontWeight.w700,
              ),
            ),
          ),
          at(
            20,
            340,
            350,
            Container(
              height: 83,
              padding: const EdgeInsets.symmetric(horizontal: 19),
              decoration: card(),
              child: Row(
                children: [
                  Container(
                    width: 43,
                    height: 43,
                    decoration: BoxDecoration(
                      color: brandSoft,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Icon(
                      Icons.schedule_rounded,
                      color: brandPrimary,
                      size: 25,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      txt('Previsão de entrega', size: 12, color: muted),
                      const SizedBox(height: 5),
                      txt('25–35 min', size: 25, weight: FontWeight.w700),
                    ],
                  ),
                ],
              ),
            ),
          ),
          at(
            24,
            441,
            342,
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                step('Recebido', true),
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 18),
                    height: 1,
                    color: lineColor,
                  ),
                ),
                step('Em preparo', false),
                Expanded(
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 18),
                    height: 1,
                    color: lineColor,
                  ),
                ),
                step('A caminho', false),
              ],
            ),
          ),
          at(
            20,
            498,
            350,
            Container(
              height: 60 + 151 * progress,
              clipBehavior: Clip.hardEdge,
              decoration: card(),
              child: Stack(
                children: [
                  Positioned(
                    left: 0,
                    right: 0,
                    top: 0,
                    height: 60,
                    child: GestureDetector(
                      key: const ValueKey('order-details'),
                      onTap: c.toggleDetails,
                      behavior: HitTestBehavior.opaque,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 17),
                        child: Row(
                          children: [
                            txt(
                              'Resumo do pedido',
                              size: 16,
                              weight: FontWeight.w700,
                            ),
                            const Spacer(),
                            Transform.rotate(
                              angle: -math.pi * progress,
                              child: const Icon(
                                Icons.keyboard_arrow_down_rounded,
                                color: brandPrimary,
                                size: 25,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    left: 17,
                    top: 65,
                    width: 316,
                    height: 140,
                    child: Opacity(
                      opacity: progress,
                      child: SingleChildScrollView(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            for (final item in order.items)
                              Padding(
                                padding: const EdgeInsets.only(bottom: 9),
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: txt(
                                        '${item.quantity}× ${item.name}',
                                        size: 12,
                                      ),
                                    ),
                                    txt(money(item.subtotal), size: 12),
                                  ],
                                ),
                              ),
                            Row(
                              children: [
                                txt('Entrega', size: 11, color: muted),
                                const Spacer(),
                                txt(
                                  money(order.deliveryFee),
                                  size: 11,
                                  color: muted,
                                ),
                              ],
                            ),
                            const SizedBox(height: 11),
                            Row(
                              children: [
                                txt('Total', size: 16, weight: FontWeight.w700),
                                const Spacer(),
                                txt(
                                  money(order.total),
                                  size: 20,
                                  color: brandDark,
                                  weight: FontWeight.w700,
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            txt(order.payment, size: 11, color: muted),
                            const SizedBox(height: 5),
                            txt(order.address, size: 11, color: muted),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          at(
            24,
            742,
            342,
            ActionButton(
              key: const ValueKey('new-order'),
              label: 'Voltar ao início',
              onTap: () => c.home(newOrder: true),
            ),
          ),
          at(
            20,
            804,
            350,
            txt(
              'Tecnologia na Prática · pedido demonstrativo',
              size: 10,
              color: muted,
              align: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget step(String label, bool active) => SizedBox(
    width: 85,
    child: Column(
      children: [
        Container(
          width: 17,
          height: 17,
          decoration: BoxDecoration(
            color: active ? brandPrimary : const Color(0xFFE1E6DC),
            shape: BoxShape.circle,
          ),
          child: active
              ? const Icon(Icons.check_rounded, color: Colors.white, size: 12)
              : null,
        ),
        const SizedBox(height: 7),
        txt(
          label,
          size: 10,
          color: active ? brandDark : muted,
          weight: active ? FontWeight.w700 : FontWeight.w400,
        ),
      ],
    ),
  );
}
