<?php

namespace Drupal\chatbot_block\Controller;

use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use GuzzleHttp\Client;
use Drupal\Core\Cache\CacheBackendInterface;


class ChatbotController {

  private $config;
  private $requestLimit;
  private $timeWindow;
  private $expiryTime;
  private $maxLength;

  public function __construct() {
    $this->config = \Drupal::config('chatbot_block.settings');
    $this->requestLimit = $this->config->get('REQUEST_LIMIT'); // Max number of requests allowed
    $this->timeWindow = $this->config->get('TIME_WINDOW'); // Time window in seconds for rate limiting
    $this->expiryTime = $this->config->get('EXPIRY_TIME'); // Time in seconds for token expiry
    $this->maxLength = $this->config->get('MAX_LENGTH');
  }




  // private const REQUEST_LIMIT = 15; // Max number of requests allowed
  // private const TIME_WINDOW = 60; // Time window in seconds for rate limiting
  // private const EXPIRY_TIME = 600; // Time in seconds for token expiry
  // private const MAX_LENGTH = 50;

  public function rate_limit(string $ip){

    $current_time = time();
    $cache = \Drupal::cache()->get('chatbot_block_ip_by_token');
    $ip_by_token = $cache ? $cache->data : [];

    foreach ($ip_by_token as $stored_ip => $ip_data) {
      if (($current_time - $ip_data['timestamp']) > $this->expiryTime) {
          unset($ip_by_token[$stored_ip]);
      }
    }
    \Drupal::cache()->set('chatbot_block_ip_by_token', $ip_by_token, CacheBackendInterface::CACHE_PERMANENT);



    if (!array_key_exists($ip, $ip_by_token) || ($current_time - $ip_by_token[$ip]['timestamp']) > $this->timeWindow) {
      $ip_by_token[$ip] = ['count' => 1, 'timestamp' => $current_time];
      \Drupal::cache()->set('chatbot_block_ip_by_token', $ip_by_token, CacheBackendInterface::CACHE_PERMANENT);
      return null; // Allow the request
  }

    if ($ip_by_token[$ip]['count'] >= $this->requestLimit) {
        return new JsonResponse(['output' => 'Veuillez attendre 1 minute avant de continuer']);
    } else {
        $ip_by_token[$ip]['count'] += 1;
        \Drupal::cache()->set('chatbot_block_ip_by_token', $ip_by_token, CacheBackendInterface::CACHE_PERMANENT);
        return null; // Allow the request
    }

  }


  public function classifyIntent(Request $request) {
    try {
      $ip = $request->getClientIp();
      $rate_limit_response = $this->rate_limit($ip);
      if ($rate_limit_response instanceof JsonResponse) {
        \Drupal::logger('chatbot_block')->error('Rate limit exceeded for IP: @ip', ['@ip' => $ip]);
        return $rate_limit_response;
  }}catch (\Exception $e) {
        \Drupal::logger('chatbot_block')->error($e->getMessage());
      }

    $client = new Client();
    $config = \Drupal::config('chatbot_block.settings');
    $api_key = $config->get('api_key');
    $classifyIntnetUrl = $config->get('api_url') . '/classify_intent_v4';
    $token = $config->get('token');
    
    // $requestData = json_decode($request->getContent(), true);
    // if (strlen($requestData['text']) > $this->maxLength){
    //   return new JsonResponse([
    //     'output' => 'Veuillez entrer un message de moins de 50 caractères.'
    //   ]);
    // }
  
    // $requestData['token'] = $token;

    // try{
    // $response = $client->post($classifyIntnetUrl, [
    //   'json' => $requestData,
    //   'headers' => [
    //     'Content-Type'=> 'application/json',
    //     'X-Api-Key' => $api_key,
    //     'Access-Control-Allow-Origin' => '*',
    //   ],
    // ]);
    
 

    // $data = json_decode($response->getBody(), TRUE);
    // $jsonResponse =  new JsonResponse($data);
    return new JsonResponse([
          'output' => 'test classify'
        ]);

  
  // }   catch (\Exception $e) {
  //   \Drupal::logger('chatbot_block')->error($e->getMessage());
  //   return new JsonResponse(['error' => 'Service unavailable'], 500);
  // }
  }


  public function requestData(Request $request) {

    $ip = $request->getClientIp();
    $rate_limit_response = $this->rate_limit($ip);

    if ($rate_limit_response instanceof JsonResponse) {
        return $rate_limit_response;
    }
    

    $client = new Client();
    $config = \Drupal::config('chatbot_block.settings');
    $api_key = $config->get('api_key');
    $requestDataUrl = $config->get('api_url') . '/req_data_v2';
    $token = $config->get('token');
  //   $requestData = json_decode($request->getContent(), true);
  //   if (!$requestData['text']) {
  //     return new JsonResponse([
  //       'output' => 'Veuillez entrer un message.'
  //     ]);
  //   }
  //   if (strlen($requestData['text']) > $this->maxLength){
  //     return new JsonResponse([
  //       'output' => 'Veuillez entrer un message de moins de 50 caractères.'
  //     ]);
  //   }

  //   $requestData['token'] = $token;

  //   try{
  //   $response = $client->post($requestDataUrl, [
  //     'json' => $requestData,
  //     'headers' => [
  //       'Content-Type'=> 'application/json',
  //       'X-Api-Key' => $api_key,
  //       'Access-Control-Allow-Origin' => '*',
  //     ],
  //   ]);

  //   $data = json_decode($response->getBody(), TRUE);
  //   $jsonResponse =  new JsonResponse($data);
  //   return $jsonResponse;

  // }   catch (\Exception $e) {
  //   \Drupal::logger('chatbot_block')->error($e->getMessage());
  //   return new JsonResponse(['error' => 'Service unavailable'], 500);
  // }
  return new JsonResponse([
    'output' => 'test request data'
  ]);
  }

  public function generalV1(Request $request) {

    $ip = $request->getClientIp();
    $rate_limit_response = $this->rate_limit($ip);

    if ($rate_limit_response instanceof JsonResponse) {
        return $rate_limit_response;
    }

    $client = new Client();
    $config = \Drupal::config('chatbot_block.settings');
    $api_key = $config->get('api_key');
    $generalV1Url = $config->get('api_url') . '/gener_v1';
    $token = $config->get('token');
  //   $requestData = json_decode($request->getContent(), true);
  //   if (!$requestData['text']) {
  //     return new JsonResponse([
  //       'output' => 'Veuillez entrer un message.'
  //     ]);
  //   }
  //   if (strlen($requestData['text']) > $this->maxLength){
  //     return new JsonResponse([
  //       'output' => 'Veuillez entrer un message de moins de 50 caractères.'
  //     ]);
  //   }

  //   $requestData['token'] = $token;
  //   try{
  //   $response = $client->post($generalV1Url, [
  //     'json' => $requestData,
  //     'headers' => [
  //       'Content-Type'=> 'application/json',
  //       'X-Api-Key' => $api_key,
  //       'Access-Control-Allow-Origin' => '*',
  //     ],
  //   ]);
    
  //   $data = json_decode($response->getBody(), TRUE);
  //   $jsonResponse =  new JsonResponse($data);
  //   return $jsonResponse;

  // }   catch (\Exception $e) {
  //   \Drupal::logger('chatbot_block')->error($e->getMessage());
  //   return new JsonResponse(['error' => 'Service unavailable'], 500);
  // }
  return new JsonResponse([
    'output' => 'test general v1'
  ]);
  }

}