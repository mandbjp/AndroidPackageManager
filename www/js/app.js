(function(){
  'use strict';
  var module = angular.module('myApp', ['onsen']);


// ===== TopCtrl =====
  module.controller('TopCtrl',
    function($scope, $http, MyPagePushService) {

      $scope.goDeviceList = function() {
        MyPagePushService.pushPage($scope, 'device_list.html');
      }

      $scope.goConnectWearDebug = function(){
        $http({
          method: 'GET',
          url: '/connect-wear-debug',
        })
        .success(function(data) {
          console.log(data);
          alert(data);
        })
        .error(function(data) {
          alert(data);
        });
      }
    }
  );

// ===== DeviceListCtrl =====
  module.controller('DeviceListCtrl',
    function($scope, $http, CacheService, MyPagePushService) {
      $scope.devices = [];

      $scope.getDeviceList = function() {
        $http({
          method: 'GET',
          url: '/devices',
        })
        .success(function(data) {
          console.log(data);
          $scope.devices = data;

        })
        .error(function(data) {
          alert(data);
        });
      }
      $scope.getDeviceList();

      $scope.goPackageList = function(device){
        CacheService.putSelectedDevice(device);
        MyPagePushService.pushPage($scope, 'package_list.html');
      }

    }
  );


// ===== PackageListCtrl =====
  module.controller('PackageListCtrl',
    function($scope, $http, CacheService, MyPagePushService) {
      $scope.packages = [];

      var selected_device = CacheService.getSelectedDevice();
      $scope.device_id = selected_device.device_id;

      $scope.getPackageList = function(device_id) {
        $http({
          method: 'GET',
          url: '/packages',
          params: {
            device_id: device_id
          }
        })
        .success(function(data) {
          console.log(data);
          $scope.packages = data.packages;

        })
        .error(function(data) {
          alert(data);
        })
        ;
      }
      $scope.getPackageList($scope.device_id);

      $scope.goPackageDetail = function(package_name){
        CacheService.putSelectedPackageName(package_name);
        MyPagePushService.pushPage($scope, 'package_detail.html');
      }

    }
  );

// ===== PackageDetailCtrl =====
  module.controller('PackageDetailCtrl',
    function($scope, $window, $http, CacheService, MyPagePushService, GooglePlayService) {

      var selected_device = CacheService.getSelectedDevice();
      $scope.device_id = selected_device.device_id;
      $scope.package_name = CacheService.getSelectedPackageName();

      $scope.goOpenPackageOnGooglePlay = function() {
        var url = 'http://play.google.com/store/apps/details?id=' + $scope.package_name;
        $window.open(url);
      }

      $scope.startPackage = function() {
        $http({
          method: 'GET',
          url: '/start-package',
          params: {
            device_id: $scope.device_id,
            package_name: $scope.package_name
          }
        })
        .success(function(data) {
          console.log(data);
          alert(data.response);

        })
        .error(function(data) {
          alert(data);
        })
        ;

      }

      $scope.uninstallPackage = function() {
        if (!confirm('are you sure to uninstall package?')){
          return;
        }
        $http({
          method: 'GET',
          url: '/uninstall-package',
          params: {
            device_id: $scope.device_id,
            package_name: $scope.package_name
          }
        })
        .success(function(data) {
          console.log(data);
          alert(data.response);

        })
        .error(function(data) {
          alert(data);
        })
        ;

      }

      var iconRequest = GooglePlayService.getPackageIconFromGooglePlay($scope.package_name, 64);
      iconRequest.success(function(data){
        console.log(data);
        $scope.app_icon = data.image_src;
      });
    }
  );




// Service --------------------------


  module.service('CacheService',
    function($cacheFactory) {
      var cache = $cacheFactory('CacheService');

      // SelectedDevice
      this.getSelectedDevice = function() {
        return cache.get('SelectedDevice');
      };
      this.putSelectedDevice = function(device) {
        cache.put('SelectedDevice', device);
      };

      // SelectedPackageName
      this.getSelectedPackageName = function() {
        return cache.get('SelectedPackageName');
      };
      this.putSelectedPackageName = function(package_name) {
        cache.put('SelectedPackageName', package_name);
      };
    }
  );


  module.service('MyPagePushService', 
    function($log){
      this.pushPage = function(scope, url) {
        $log.debug(url);
        var timestamp = new Date().getTime();
        var push_url = url + ((url.indexOf('&') === -1) ? '?': '&') + 'timestamp=' + timestamp;
        scope.ons.navigator.pushPage(push_url);
      }
    }
  );

  module.service('GooglePlayService',
    function($log, $http){

      // Get icon from Google Play
      this.getPackageIconFromGooglePlay = function(package_name, icon_size){
        var url = '/package-icon';
        var size = icon_size || 48;
        return $http({
          method: 'GET',
          url: url,
          params: {
            package_name: package_name,
            icon_size: size
          }
        });
      }
    }
  );
})();

