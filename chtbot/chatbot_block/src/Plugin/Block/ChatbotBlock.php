<?php

namespace Drupal\chatbot_block\Plugin\Block;

use Drupal\Core\Block\BlockBase;
use Drupal\Core\Url;
use Drupal\Core\Entity\EntityTypeManager;
use Drupal\Core\Language\LanguageManagerInterface;



/**
 * Provides a 'Chatbot' Block.
 *
 * @Block(
 *   id = "chatbot",
 *   admin_label = @Translation("Chatbot"),
 *   category = @Translation("chatbot"),
 * )
 */
class ChatbotBlock extends BlockBase {

  /**
   * {@inheritdoc}
   */
  public function build() {
    $build = [];
    $image_path = \Drupal::service('extension.list.module')->getPath('chatbot_block') . '/images/datagv.png';
    $image_url = \Drupal::service('file_url_generator')->generateAbsoluteString($image_path);

    $trbch_path = \Drupal::service('extension.list.module')->getPath('chatbot_block') . '/images/trbch.png';
    $trbch_url = \Drupal::service('file_url_generator')->generateAbsoluteString($trbch_path);

    \Drupal::logger('chatbot_block')->notice('Image URL: @url', ['@url' => $trbch_url]);

    $language_code = \Drupal::service('language_manager')->getCurrentLanguage()->getId();
    \Drupal::logger('chatbot_block')->notice('language: @url', ['@url' => $language_code]);

    if ($language_code === 'ar') {
      // Attach Arabic-specific CSS.
      $library = 'chatbot_block/chatbot_css_arabic';
    } else {
      // Attach default CSS for other languages.
      $library = 'chatbot_block/chatbot_css_french';
    }



    $build['chatbot'] = [
      '#theme' => 'chatbot',
      '#title' => 'chatbot',
      '#image_url' => $image_url,
      '#trbch_url' => $trbch_url,
      '#attached' => [
        'library' => [
          $library,
        ],
        'drupalSettings' => [
          'chatbot_block' => [
            'languageCode' => $language_code,
          ],
        ],
      ],

    ];

    return $build;
  }
}