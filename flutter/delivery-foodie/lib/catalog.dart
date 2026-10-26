class Product {
  const Product(
    this.id,
    this.name,
    this.price,
    this.art,
    this.category,
    this.description,
    this.minutes,
  );
  final String id, name, category, description;
  final int price, art, minutes;
}

const products = <Product>[
  Product(
    'burger',
    'Hambúrguer da casa',
    2990,
    0,
    'Burgers',
    'Pão macio com gergelim, hambúrguer grelhado, cheddar, alface e tomate. Feito na hora, do jeito que você gosta.',
    25,
  ),
  Product(
    'pizza',
    'Pizza de pepperoni',
    2490,
    1,
    'Pizza',
    'Massa leve, queijo derretido e pepperoni. Uma fatia generosa para matar a fome.',
    20,
  ),
  Product(
    'fries',
    'Batata crocante',
    1490,
    2,
    'Batatas',
    'Batatas douradas, crocantes por fora e macias por dentro. A companhia perfeita para seu pedido.',
    15,
  ),
  Product(
    'sushi',
    'Combo de salmão',
    3490,
    3,
    'Sushi',
    'Seleção de makis de salmão, preparados na hora. Acompanha hashis.',
    30,
  ),
  Product(
    'juice',
    'Suco de laranja',
    990,
    4,
    'Bebidas',
    'Suco de laranja gelado, refrescante e preparado para acompanhar sua refeição.',
    10,
  ),
  Product(
    'chicken',
    'Frango crocante',
    2790,
    5,
    'Frango',
    'Frango empanado com casquinha dourada e tempero da casa. Servido bem quentinho.',
    25,
  ),
];
const categories = [
  'Todos',
  'Burgers',
  'Pizza',
  'Batatas',
  'Sushi',
  'Bebidas',
  'Frango',
];
const categoryArt = [0, 0, 1, 2, 3, 4, 5];
