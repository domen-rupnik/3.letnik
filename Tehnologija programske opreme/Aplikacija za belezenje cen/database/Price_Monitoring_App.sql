-- phpMyAdmin SQL Dump
-- version 4.9.5
-- https://www.phpmyadmin.net/
--
-- Gostitelj: localhost:3306
-- Čas nastanka: 07. jan 2021 ob 11.52
-- Različica strežnika: 10.3.27-MariaDB-cll-lve
-- Različica PHP: 7.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Zbirka podatkov: `skijavornik_tpo4`
--

-- --------------------------------------------------------

--
-- Struktura tabele `Price_`
--

CREATE TABLE `Price_` (
  `price_id` int(11) NOT NULL,
  `price_product_shop_id` int(11) NOT NULL,
  `price_price` decimal(10,2) NOT NULL,
  `price_date` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Sprožilci `Price_`
--
DELIMITER $$
CREATE TRIGGER `product_price_update` AFTER INSERT ON `Price_` FOR EACH ROW BEGIN
    -- Posodobimo ceno izdelka
    UPDATE Product_Shop_
    SET product_shop_price = new.price_price
    WHERE product_shop_id = new.price_product_shop_id;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktura tabele `Product_`
--

CREATE TABLE `Product_` (
  `product_id` int(11) NOT NULL,
  `product_name` varchar(300) DEFAULT NULL,
  `product_image` varchar(300) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Sprožilci `Product_`
--
DELIMITER $$
CREATE TRIGGER `edigital_image` BEFORE INSERT ON `Product_` FOR EACH ROW begin
IF(LOCATE('static', new.product_image) != 0) THEN
	SET new.product_image = CONCAT("http:", new.product_image);
end if;
end
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktura tabele `Product_Shop_`
--

CREATE TABLE `Product_Shop_` (
  `product_shop_id` int(11) NOT NULL,
  `product_shop_product_id` int(11) NOT NULL,
  `product_shop_shop_name` varchar(30) NOT NULL,
  `product_shop_url` varchar(300) NOT NULL,
  `product_shop_price` decimal(10,2) NOT NULL,
  `product_shop_discount` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Struktura tabele `Shop_`
--

CREATE TABLE `Shop_` (
  `shop_name` varchar(30) NOT NULL,
  `shop_url` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Odloži podatke za tabelo `Shop_`
--

INSERT INTO `Shop_` (`shop_name`, `shop_url`) VALUES
('Big Bang', 'bigbang.si'),
('Extreme Digital', 'edigital.si'),
('Mimovrste', 'mimovrste.com');

-- --------------------------------------------------------

--
-- Struktura tabele `Users_Products_`
--

CREATE TABLE `Users_Products_` (
  `users_products_user_id` int(11) NOT NULL,
  `users_products_product_id` int(11) NOT NULL,
  `users_products_lower_reminder` decimal(10,2) DEFAULT NULL,
  `users_products_upper_reminder` decimal(10,2) DEFAULT NULL,
  `users_products_lower_condition` tinyint(1) DEFAULT NULL,
  `users_products_upper_condition` tinyint(1) DEFAULT NULL,
  `users_products_sent_email` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


--
-- Struktura tabele `User_`
--

CREATE TABLE `User_` (
  `user_id` int(11) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `user_surname` varchar(50) NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `user_password` varchar(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Indeksi zavrženih tabel
--

--
-- Indeksi tabele `Price_`
--
ALTER TABLE `Price_`
  ADD PRIMARY KEY (`price_id`),
  ADD KEY `FK_Price_for_Product` (`price_product_shop_id`);

--
-- Indeksi tabele `Product_`
--
ALTER TABLE `Product_`
  ADD PRIMARY KEY (`product_id`);

--
-- Indeksi tabele `Product_Shop_`
--
ALTER TABLE `Product_Shop_`
  ADD PRIMARY KEY (`product_shop_id`),
  ADD KEY `FK_Shop_for_Product` (`product_shop_shop_name`),
  ADD KEY `FK_Sub_Products` (`product_shop_product_id`);

--
-- Indeksi tabele `Shop_`
--
ALTER TABLE `Shop_`
  ADD PRIMARY KEY (`shop_name`);

--
-- Indeksi tabele `Users_Products_`
--
ALTER TABLE `Users_Products_`
  ADD PRIMARY KEY (`users_products_user_id`,`users_products_product_id`),
  ADD KEY `FK_Users_Products2` (`users_products_product_id`);

--
-- Indeksi tabele `User_`
--
ALTER TABLE `User_`
  ADD PRIMARY KEY (`user_id`);

--
-- Omejitve tabel za povzetek stanja
--

--
-- Omejitve za tabelo `Price_`
--
ALTER TABLE `Price_`
  ADD CONSTRAINT `FK_Price_for_Product` FOREIGN KEY (`price_product_shop_id`) REFERENCES `Product_Shop_` (`product_shop_id`);

--
-- Omejitve za tabelo `Product_Shop_`
--
ALTER TABLE `Product_Shop_`
  ADD CONSTRAINT `FK_Shop_for_Product` FOREIGN KEY (`product_shop_shop_name`) REFERENCES `Shop_` (`shop_name`),
  ADD CONSTRAINT `FK_Sub_Products` FOREIGN KEY (`product_shop_product_id`) REFERENCES `Product_` (`product_id`);

--
-- Omejitve za tabelo `Users_Products_`
--
ALTER TABLE `Users_Products_`
  ADD CONSTRAINT `FK_Users_Products` FOREIGN KEY (`users_products_user_id`) REFERENCES `User_` (`user_id`),
  ADD CONSTRAINT `FK_Users_Products2` FOREIGN KEY (`users_products_product_id`) REFERENCES `Product_` (`product_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
